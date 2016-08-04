import pytest

from exercises import Exercise


def test_list():
    exercises = Exercise.list()
    assert isinstance(exercises, list)
    names = [x.name for x in exercises]
    assert 'example_python' in names
    assert '__pycache__' not in names
