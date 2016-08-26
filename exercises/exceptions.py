
class NotExists(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Exercise with name={0.name} not found".format(self)
