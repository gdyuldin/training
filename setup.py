import os
import re

from setuptools import find_packages, setup


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(
        os.path.dirname(__file__), 'training_backend', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            msg = 'Cannot find version in training_backend/__init__.py'
            raise RuntimeError(msg)


install_requires = ['aiohttp', 'pyyaml', 'docker-py', 'pytest-runner']
tests_require = ['pytest', 'pyhamcrest', 'pytest-asyncio']

setup(
    name='training_backend',
    version=read_version(),
    description='Education portal trainig backend',
    platforms=['POSIX'],
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    zip_safe=False)
