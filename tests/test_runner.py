import pathlib

import pytest
from hamcrest import assert_that, has_entries, instance_of

from exercises import Exercise
from exercises.utils import Runner


@pytest.fixture
def runner():
    return Runner()


@pytest.fixture
def image_path():
    return str(pathlib.Path(__file__).parent / 'runner_test_data')


@pytest.fixture
def extra_dir(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("hello.txt")
    p.write("content")
    return tmpdir


@pytest.yield_fixture()
def image(runner, image_path):
    image = runner._build_image(image_path, tag='test_image')
    yield image
    runner.cli.remove_image('test_image', force=True)


@pytest.yield_fixture(autouse=True)
def clean_docker(runner):
    cli = runner.cli
    images_tags = {x for y in cli.images() for x in y['RepoTags']}

    container_ids = {x['Id'] for x in cli.containers(all=True, quiet=True)}

    yield

    # Cleanup containers
    new_container_ids = {x['Id'] for x in cli.containers(all=True, quiet=True)}
    for container_id in new_container_ids - container_ids:
        cli.remove_container(container_id, force=True)

    # Cleanup images
    new_images_tags = {x for y in cli.images() for x in y['RepoTags']}
    for image_tag in new_images_tags - images_tags:
        cli.remove_image(image_tag, force=True)


def test_docker_connect(runner):
    assert runner.cli.version() is not None


def test_build_image(runner, image_path):
    runner._build_image(image_path)
    assert len(runner.cli.images(name='runner_test_data')) == 1


def test_build_image_with_tag(runner, image_path):
    runner._build_image(image_path, tag='some_tag')
    assert len(runner.cli.images(name='some_tag')) == 1


def test_create_container(runner):
    container = runner._create_container('busybox')
    assert_that(container, has_entries('Id', instance_of(str)))


def test_create_container_with_data(runner, extra_dir, image):
    container = runner._create_container(image, [str(extra_dir)])
    runner.cli.start(container=container.get('Id'))
    stdout = runner.cli.logs(container, stderr=False)
    stderr = runner.cli.logs(container, stdout=False)
    assert b"sub/hello.txt" in stdout
    assert len(stderr) == 0


def test_run(runner, image_path, extra_dir):
    container_id = runner._start(image_path, extra_dirs=[str(extra_dir)])
    assert_that(container_id, instance_of(str))


def test_start_exercise_checking(runner):
    ex = Exercise('example_python')
    data = {'answer.py': 'get_max = lambda x: x[0]'}
    container_id = runner.start_exercise_checking(ex, data)
    assert container_id is not None


def test_get_result(runner):
    ex = Exercise('example_python')
    data = {'answer.py': 'get_max = lambda x: x[0]'}
    container_id = runner.start_exercise_checking(ex, data)
    exit_code, stdout, stderr = runner.get_results(container_id, timeout=30)
    assert_that(exit_code, instance_of(int))
    assert_that(stdout, instance_of(bytes))
    assert_that(stderr, instance_of(bytes))
    assert len(runner.cli.containers(filters={'id': container_id})) == 0
