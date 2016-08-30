import pathlib

import pytest
from hamcrest import assert_that, has_properties, instance_of, not_, contains

from exercises import Exercise
from exercises.utils import Runner


@pytest.yield_fixture
def runner(event_loop):
    runner = Runner(loop=event_loop)
    with runner.open_session():
        yield runner


@pytest.fixture
def image_path():
    return str(pathlib.Path(__file__).parent / 'runner_test_data')


@pytest.fixture
def extra_dir(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("hello.txt")
    p.write("content")
    return tmpdir


@pytest.fixture
def image(runner, image_path, event_loop):
    image = event_loop.run_until_complete(
        runner._build_image(image_path, tag='test_image'))
    return image


@pytest.yield_fixture(autouse=True)
def clean_docker(runner, event_loop):
    async def inspect():
        images = await runner.api.Image.list()
        images_tags = {x for y in images for x in y.data.repo_tags}
        containers = await runner.api.Container.list()
        container_ids = {x.id for x in containers}
        return images_tags, container_ids

    images_tags, container_ids = event_loop.run_until_complete(inspect())

    yield

    new_images_tags, new_container_ids = event_loop.run_until_complete(inspect())

    async def cleanup(ids, class_name):
        for _id in ids:
            await getattr(runner.api, class_name)(_id).remove(force=True)

    event_loop.run_until_complete(cleanup(new_container_ids - container_ids, 'Container'))
    event_loop.run_until_complete(cleanup(new_images_tags - images_tags, 'Image'))


@pytest.mark.asyncio
async def test_docker_connect(runner):
    containers = await runner.api.Container.list()
    assert isinstance(containers, list)


@pytest.mark.asyncio
async def test_build_image(runner, image_path, event_loop):
    await runner._build_image(image_path)
    images = await runner.api.Image.list(filter='runner_test_data')
    assert len(images) == 1


@pytest.mark.asyncio
async def test_build_image_with_tag(runner, image_path):
    await runner._build_image(image_path, tag='some_tag')
    images = await runner.api.Image.list(filter='some_tag')
    assert len(images) == 1


@pytest.mark.asyncio
async def test_create_container(runner):
    container = await runner._create_container('busybox')
    assert_that(container.id, instance_of(str))


@pytest.mark.asyncio
async def test_delete_container(runner):
    container = await runner._create_container('busybox')
    await container.inspect()

    await runner._remove_container(container.id)
    with pytest.raises(Exception):
        await container.inspect()


@pytest.mark.asyncio
async def test_create_container_with_data(runner, extra_dir, image):
    image_tag = image.data.repo_tags[0]
    container = await runner._create_container(image_tag, [str(extra_dir)])
    await container.start()
    stdout = await container.logs(stdout=True)
    stderr = await container.logs(stderr=True)
    assert "sub/hello.txt" in stdout.decode()
    assert len(stderr) == 0


@pytest.mark.asyncio
async def test_run(runner, image_path, extra_dir):
    container_id = await runner._start(image_path, extra_dirs=[str(extra_dir)])
    assert_that(container_id, instance_of(str))


@pytest.mark.asyncio
async def test_start_exercise_checking(runner):
    ex = Exercise('example_python')
    data = {'answer.py': 'get_max = lambda x: x[0]'}
    container_id = await runner.start_exercise_checking(ex, data)
    assert container_id is not None


@pytest.mark.asyncio
async def test_get_result(runner):
    ex = Exercise('example_python')
    data = {'answer.py': 'get_max = lambda x: x[0]'}
    container_id = await runner.start_exercise_checking(ex, data)
    exit_code, stdout, stderr = await runner.get_results(container_id, timeout=30)
    assert_that(exit_code, instance_of(int))
    assert_that(stdout, instance_of(bytes))
    assert_that(stderr, instance_of(bytes))
    containers = await runner.api.Container.list()
    assert_that(containers, not_(contains(has_properties(id=container_id))))
