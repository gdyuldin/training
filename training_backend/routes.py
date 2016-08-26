from .views import exercises_list
from .views import check_exercise


def setup_routes(app):
    app.router.add_route('GET', '/exercises', exercises_list)
    app.router.add_route('POST',
                         '/exercises/{name}',
                         check_exercise,
                         name='check_exercise')
