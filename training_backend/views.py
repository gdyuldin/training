from aiohttp import web
import exercises


async def exercises_list(request):
    ex_list = [x.to_dict() for x in exercises.Exercise.list()]
    return web.json_response({'exercises': ex_list})


async def check_exercise(request):
    try:
        ex = exercises.Exercise(request.match_info['name'])
    except exercises.NotExists:
        raise web.HTTPNotFound()
    payload = await request.json()
    for name in ex.answer_files:
        if name not in payload:
            raise web.HTTPBadRequest
    runner = exercises.utils.Runner()
    exit_code, stdout, stderr = runner.check_exercise(ex, payload)
    return web.json_response({
        'check_result': {
            'exit_code': exit_code,
            'stdout': stdout.decode(),
            'stderr': stderr.decode()
        }
    })
