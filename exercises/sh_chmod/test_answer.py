import os
import subprocess

import pytest

BASE_DIR = os.path.dirname(__file__)


@pytest.fixture
def testdata():
    return os.path.join(BASE_DIR, 'testdata')


@pytest.fixture
def reset_access(testdata):
    for name in os.listdir(testdata):
        os.chmod(os.path.join(testdata, name), 777)


def test_answer(reset_access, testdata):
    subprocess.check_call([os.path.join(BASE_DIR, 'answer.sh')], cwd=testdata)
    for name in os.listdir(testdata):
        print(name)
        path = os.path.join(testdata, name)
        mode = oct(os.stat(path).st_mode)
        if os.path.isdir(path):
            assert mode.endswith('755')
        elif os.path.isfile(path):
            assert mode.endswith('644')
