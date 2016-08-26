import types

from hamcrest import only_contains, instance_of, assert_that, has_entries
import pytest

from exercises import Exercise


@pytest.fixture
def example_python():
    return Exercise('example_python')


@pytest.fixture
def example_sh():
    return Exercise('example_sh')


def test_list():
    exercises = Exercise.list()
    assert isinstance(exercises, list)
    names = [x.name for x in exercises]
    assert 'example_python' in names
    assert '__pycache__' not in names


def test_exercise_doc(example_python):
    assert '1111111' in example_python.__doc__


def test_exercise_wo_doc(example_sh):
    assert 'No README for exercise' == example_sh.__doc__


def test_prepare_module(example_python):
    assert isinstance(example_python.settings, types.ModuleType)


def test_image(example_python):
    assert example_python.image == 'images/pytest'


def test_defaul_image(example_sh):
    assert example_sh.image == 'images/pytest'


def test_answers_list(example_sh):
    assert 'answer.sh' in example_sh.answer_files


def test_to_dict(example_python):
    data = example_python.to_dict()
    assert_that(data,
                has_entries(name='example_python',
                            doc=instance_of(str),
                            answers=only_contains(instance_of(str))))
