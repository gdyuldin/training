import os
import time
import subprocess
import pytest

BASE_DIR = os.path.dirname(__file__)


@pytest.yield_fixture
def daemon():
    p = subprocess.Popen(['python', os.path.join(BASE_DIR, 'daemon.py')])
    # Time for start
    time.sleep(1)
    yield p
    p.kill()


def get_path(p):
    pid = p.pid
    cmd = "lsof +p {} | grep /tmp | head -n1 | awk '{{print $9}}'".format(pid)
    return subprocess.check_output(cmd, shell=True)


def test_answer(daemon):
    expected = get_path(daemon)
    result = subprocess.check_output([os.path.join(BASE_DIR, 'answer.sh')])
    assert result.strip() == expected.strip()
