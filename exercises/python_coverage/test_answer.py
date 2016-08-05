import os
import subprocess
import coverage

BASE_DIR = os.path.dirname(__file__)


def test_coverage():
    answer_path = os.path.join(BASE_DIR, 'answer.py')
    subprocess.check_call(
        ['coverage', 'run', '--branch', '-m', 'unittest', answer_path],
        cwd=BASE_DIR)
    cov_data = coverage.CoverageData()
    cov_data.read_file(os.path.join(BASE_DIR, '.coverage'))
    assert cov_data.line_counts()['function.py'] == 4
