import asyncio
import contextlib
import shutil
import tempfile
import io
import logging
import pathlib
import tarfile

from asyncio_docker import api as docker_api
from asyncio_docker import client as docker_client

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def clone_dir(source):
    temp_dir = tempfile.mktemp(suffix='_answers')
    shutil.copytree(source, temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


class Runner(object):
    def __init__(self, docker_url='unix://var/run/docker.sock', loop=None):
        client_class = docker_client.client_factory(docker_url)
        self.client = client_class(docker_url, loop=loop)

    @contextlib.contextmanager
    def open_session(self):
        with self.client:
            self.api = docker_api.RemoteAPI(self.client)
            yield

    async def _put_data(self, container, path, dirs=()):
        if len(dirs) == 0:
            return
        buf = io.BytesIO()
        with tarfile.open(mode='w', fileobj=buf) as tar:
            for d in dirs:
                tar.add(d, arcname='')
        buf.seek(0)
        await container.put_archive(path, buf.read())

    async def _build_image(self, path, tag=None):
        tag = tag or pathlib.Path(path).parts[-1]
        buf = io.BytesIO()
        with tarfile.open(mode='w', fileobj=buf) as tar:
            tar.add(path, arcname='')
        buf.seek(0)
        image = await self.api.Image.build(buf, t=tag)
        return image

    async def _create_container(self, image_tag, extra_dirs=()):
        images = await self.api.Image.list(filter=image_tag)
        image = images[0]
        image_data = await image.inspect()

        container = await self.api.Container.create({'Image': image_tag})
        container_workdir = image_data['Config']['WorkingDir']
        await self._put_data(container, container_workdir, extra_dirs)
        return container

    async def _wait_for_done(self, container_id):
        while True:
            container = self.api.Container(container_id)

            container_data = await container.inspect()
            if container_data['State']['Running'] is not True:
                break
        return container

    async def _remove_container(self, container_id):
        container = self.api.Container(id=container_id)
        await container.remove(force=True)

    async def _start(self, image_path, extra_dirs):
        image = await self._build_image(image_path)
        image_tag = image.data.repo_tags[0]
        container = await self._create_container(image_tag, extra_dirs)
        await container.start()
        return container.id

    async def start_exercise_checking(self, exercise, data):
        """Check exercise with docker and return container_id
        :param exercise: exercise.Exercise instance
        :param data: dict with files' names and they contents
        :return: string (container_id)
        """
        with exercise.compose(data) as temp_dir:
            container_id = await self._start(exercise.image, extra_dirs=[temp_dir])
            return container_id

    async def get_results(self, container_id, timeout=1):
        try:
            fut = self._wait_for_done(container_id)
            container = await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            return
        stdout = await container.logs(stdout=True)
        stderr = await container.logs(stderr=True)
        container_data = await container.inspect()
        exit_code = container_data['State']['ExitCode']
        await self._remove_container(container_id)
        return exit_code, stdout, stderr
