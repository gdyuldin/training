import contextlib
import importlib
import os

from . import utils


class NotExists(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Exercise with name={0.name} not found".format(self)


class Exercise(object):
    """Base class for exercise"""
    BASE_DIR = os.path.dirname(__file__)
    DEFAULT_IMAGE = 'images/pytest'

    def __init__(self, name):
        if not self._is_exercise(name):
            raise NotExists(name)
        self.name = name
        self._settings = None

    @classmethod
    def _is_exercise(cls, name):
        """Check that exercise folder exists and contains `settings.py`"""
        path = os.path.join(cls.BASE_DIR, name)
        return os.path.isdir(path) and 'settings.py' in os.listdir(path)

    @property
    def _exercise_dir(self):
        return os.path.join(self.BASE_DIR, self.name)

    @property
    def settings(self):
        if self._settings is None:
            self._settings = importlib.import_module(
                '.{0.name}.settings'.format(self), __package__)
        return self._settings

    @property
    def image(self):
        return getattr(self.settings, 'IMAGE', self.DEFAULT_IMAGE)

    @property
    def __doc__(self):
        for f in os.listdir(self._exercise_dir):
            if 'README' in f:
                break
        else:
            return 'No README for exercise'
        with open(os.path.join(self._exercise_dir, f)) as f:
            return f.read()

    @property
    def answer_files(self):
        return self.settings.ANSWERS

    @classmethod
    def list(cls):
        exercises = []
        for f in os.listdir(cls.BASE_DIR):
            if cls._is_exercise(f):
                obj = cls(name=f)
                exercises.append(obj)
        return exercises

    @contextlib.contextmanager
    def compose(self, data):
        """Make temp workspace with user answer

        Delete created workspace after exitin from contextmanager.

        :param data: dict with files' names and they contents
        :return: path to temp folder with prepared worspace
        """
        src_dir = self._exercise_dir
        with utils.clone_dir(src_dir) as tempdir:
            for answer_file in self.answer_files:
                filename = answer_file['name']
                content = data[filename]
                path = os.path.join(tempdir, filename)
                with open(path, 'w') as f:
                    f.write(content)
                os.chmod(path, answer_file.get('mode', 755))
            yield tempdir
