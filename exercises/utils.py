import contextlib
import shutil
import tempfile


@contextlib.contextmanager
def clone_dir(source):
    temp_dir = tempfile.mktemp(suffix='_answers')
    shutil.copytree(source, temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)
