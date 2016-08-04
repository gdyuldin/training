#!/usr/bin/env python3

import contextlib
import io
import logging
import os
import tarfile

from docker import Client
import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

cli = Client(base_url='unix://var/run/docker.sock')


def build_image(path, tag=None):
    tag = tag or os.path.split(path)[-1]
    output = cli.build(path, tag=tag)
    for line in output:
        logger.debug(line.decode())
    return tag


def put_data(container, path, dirs=()):
    buf = io.BytesIO()
    with tarfile.open(mode='w', fileobj=buf) as tar:
        for d in dirs:
            tar.add(d, arcname='')
    buf.seek(0)
    cli.put_archive(container, path, buf.read())


@contextlib.contextmanager
def create_container(image_name, extra_dirs=()):
    image_data = cli.inspect_image(image_name)

    container = cli.create_container(image_name)
    container_workdir = image_data['Config']['WorkingDir']
    put_data(container, container_workdir, extra_dirs)
    yield container
    cli.remove_container(container=container['Id'], force=True)


def run(image_path, extra_dirs):
    image_name = build_image(image_path)
    with create_container(image_name, extra_dirs) as container:
        cli.start(container)
        try:
            cli.wait(container, timeout=10 * 60)
        except requests.exceptions.ReadTimeout:
            cli.kill(container)
        stdout = cli.logs(container, stderr=False)
        stderr = cli.logs(container, stdout=False)
        exit_code = cli.inspect_container(container)['State']['ExitCode']
    return exit_code, stdout, stderr

from exercises import utils

content = """\
import os
import time
print('Hello')
print(__file__)

def get_max(numbers):
    ints = []
    for n in numbers:
        try:
            ints.append(int(n))
        except ValueError:
            pass
    return ints and max(ints) or None
"""

with utils.compose('example_python', answer=content) as temp_dir:
    result = run('images/pytest', extra_dirs=[temp_dir])

print(result[0])
print(result[1].decode())
print(result[2].decode())
