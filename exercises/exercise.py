import importlib
import os


class Exercise(object):

    def __init__(self, name):
        self.name = name
        # TODO make exercise initialization

    @classmethod
    def list(cls):
        BASE_DIR = os.path.dirname(__file__)
        exercises = []
        for f in os.listdir(BASE_DIR):
            if not os.path.isdir(os.path.join(BASE_DIR, f)):
                continue
            if 'prepare.py' in os.listdir(os.path.join(BASE_DIR, f)):
                obj = cls(name=f)
                exercises.append(obj)
        return exercises

    def compose(self, **kwargs):
        module = importlib.import_module('.{0.name}.prepare'.format(self), __package__)
        return module.compose(**kwargs)
