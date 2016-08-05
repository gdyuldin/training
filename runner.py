#!/usr/bin/env python3

import contextlib
import io
import logging
import os
import tarfile

from docker import Client
import requests

from exercises import Exercise

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class Runner(object):
    def __init__(self, docker_url='unix://var/run/docker.sock'):
        self.cli = Client(base_url=docker_url)

    def _build_image(self, path, tag=None):
        tag = tag or os.path.split(path)[-1]
        output = self.cli.build(path, tag=tag)
        for line in output:
            logger.debug(line.decode())
        return tag

    def _put_data(self, container, path, dirs=()):
        buf = io.BytesIO()
        with tarfile.open(mode='w', fileobj=buf) as tar:
            for d in dirs:
                tar.add(d, arcname='')
        buf.seek(0)
        self.cli.put_archive(container, path, buf.read())

    @contextlib.contextmanager
    def _create_container(self, image_name, extra_dirs=()):
        image_data = self.cli.inspect_image(image_name)

        container = self.cli.create_container(image_name)
        container_workdir = image_data['Config']['WorkingDir']
        self._put_data(container, container_workdir, extra_dirs)
        yield container
        self.cli.remove_container(container=container['Id'], force=True)

    def _run(self, image_path, extra_dirs):
        image_name = self._build_image(image_path)
        with self._create_container(image_name, extra_dirs) as container:
            self.cli.start(container)
            try:
                self.cli.wait(container, timeout=10 * 60)
            except requests.exceptions.ReadTimeout:
                self.cli.kill(container)
            stdout = self.cli.logs(container, stderr=False)
            stderr = self.cli.logs(container, stdout=False)
            exit_code = self.cli.inspect_container(container)['State'][
                'ExitCode']
        return exit_code, stdout, stderr

    def check_exercise(self, exercise, data):
        """Check exercise with docker and return exit code, stout, stderr

        :param exercise: exercise.Exercise instance
        :param data: dict with files' names and they contents
        :return: tuple (exit_code, stdout, stderr)
        """
        with exercise.compose(data) as temp_dir:
            return self._run(exercise.image, extra_dirs=[temp_dir])


if __name__ == '__main__':
    runner = Runner()

    content = """
def get_max(numbers):
    ints = []
    for n in numbers:
        try:
            ints.append(int(n))
        except ValueError:
            pass
    return ints and max(ints) or None
    """
    exercise = Exercise(name='example_python')
    data = {'answer.py': content}
    result = runner.check_exercise(exercise, data)

    print(result[0])
    print(result[1].decode())
    print(result[2].decode())
