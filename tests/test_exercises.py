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
