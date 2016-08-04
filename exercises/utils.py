import contextlib
import shutil
import tempfile

from . import Exercise


@contextlib.contextmanager
def clone_dir(source):
    temp_dir = tempfile.mktemp(suffix='_answers')
    shutil.copytree(source, temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


def compose(module_name, **kwargs):
    exercise = Exercise(name=module_name)
    return exercise.compose(**kwargs)
