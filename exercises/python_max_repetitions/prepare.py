import contextlib
import os

from .. import utils


@contextlib.contextmanager
def compose(answer):
    """Make temp workspace with user answer

    Delete created workspace after exitin from contextmanager.

    :param answer: string with user answer
    :return: path to temp folder with prepared worspace
    """
    src_dir = os.path.dirname(__file__)
    filename = 'answer.py'
    with utils.clone_dir(src_dir) as tempdir:
        with open(os.path.join(tempdir, filename), 'w') as f:
            f.write(answer)
        yield tempdir
