import importlib
import os


class NotExists(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Exercise with name={0.name} not found".format(self)


class Exercise(object):
    """Base class for exercise"""
    BASE_DIR = os.path.dirname(__file__)

    def __init__(self, name):
        if not self._is_exercise(name):
            raise NotExists(name)
        self.name = name

    @classmethod
    def _is_exercise(cls, name):
        """Check that exercise folder exists and contains `prepare.py`"""
        path = os.path.join(cls.BASE_DIR, name)
        return os.path.isdir(path) and 'prepare.py' in os.listdir(path)

    @property
    def _exercise_dir(self):
        return os.path.join(self.BASE_DIR, self.name)

    @property
    def __doc__(self):
        for f in os.listdir(self._exercise_dir):
            if 'README' in f:
                break
        else:
            return 'No README for exercise'
        with open(os.path.join(self._exercise_dir, f)) as f:
            return f.read()

    @classmethod
    def list(cls):
        exercises = []
        for f in os.listdir(cls.BASE_DIR):
            if not os.path.isdir(os.path.join(cls.BASE_DIR, f)):
                continue
            if 'prepare.py' in os.listdir(os.path.join(cls.BASE_DIR, f)):
                obj = cls(name=f)
                exercises.append(obj)
        return exercises

    def compose(self, **kwargs):
        module = importlib.import_module('.{0.name}.prepare'.format(self),
                                         __package__)
        return module.compose(**kwargs)
