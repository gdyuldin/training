import contextlib
import shutil
import tempfile
import importlib


@contextlib.contextmanager
def clone_dir(source):
    temp_dir = tempfile.mktemp(suffix='_answers')
    shutil.copytree(source, temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


def compose(module_name, **kwargs):
    module = importlib.import_module('.' + module_name + '.prepare', __package__)
    return module.compose(**kwargs)
