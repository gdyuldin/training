import contextlib
import shutil
import tempfile
import io
import logging
import pathlib
import tarfile

from docker import Client
import requests

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def clone_dir(source):
    temp_dir = tempfile.mktemp(suffix='_answers')
    shutil.copytree(source, temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


class Runner(object):
    def __init__(self, docker_url='unix://var/run/docker.sock'):
        self.cli = Client(base_url=docker_url)

    def _build_image(self, path, tag=None):
        tag = tag or pathlib.Path(path).parts[-1]
        output = self.cli.build(path, tag=tag)
        for line in output:
            logger.debug(line.decode())
        return tag

    def _put_data(self, container, path, dirs=()):
        if len(dirs) == 0:
            return
        buf = io.BytesIO()
        with tarfile.open(mode='w', fileobj=buf) as tar:
            for d in dirs:
                tar.add(d, arcname='')
        buf.seek(0)
        self.cli.put_archive(container, path, buf.read())

    def _create_container(self, image_name, extra_dirs=()):
        image_data = self.cli.inspect_image(image_name)

        container = self.cli.create_container(image_name)
        container_workdir = image_data['Config']['WorkingDir']
        self._put_data(container, container_workdir, extra_dirs)
        return container

    def _remove_container(self, container_id):
        self.cli.remove_container(container=container_id, force=True)

    def _start(self, image_path, extra_dirs):
        image_name = self._build_image(image_path)
        container = self._create_container(image_name, extra_dirs)
        self.cli.start(container)
        return container['Id']

    def start_exercise_checking(self, exercise, data):
        """Check exercise with docker and return container_id

        :param exercise: exercise.Exercise instance
        :param data: dict with files' names and they contents
        :return: string (container_id)
        """
        with exercise.compose(data) as temp_dir:
            return self._start(exercise.image, extra_dirs=[temp_dir])

    def get_results(self, container_id, timeout=1):
        try:
            self.cli.wait(container_id, timeout=timeout)
        except requests.exceptions.ReadTimeout:
            return
        stdout = self.cli.logs(container_id, stderr=False)
        stderr = self.cli.logs(container_id, stdout=False)
        exit_code = self.cli.inspect_container(container_id)['State'][
            'ExitCode']
        self._remove_container(container_id)
        return exit_code, stdout, stderr
