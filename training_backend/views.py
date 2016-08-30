import uuid
import json

from aiohttp import web
import exercises


async def exercises_list(request):
    ex_list = [x.to_dict() for x in exercises.Exercise.list()]
    return web.json_response({'exercises': ex_list})


async def check_exercise(request):
    try:
        exercise_name = request.match_info['name']
        ex = exercises.Exercise(exercise_name)
    except exercises.NotExists:
        raise web.HTTPNotFound()
    payload = await request.json()
    for name in ex.answer_files:
        if name not in payload:
            raise web.HTTPBadRequest
    runner = exercises.utils.Runner()
    container_id = runner.start_exercise_checking(ex, payload)
    taks_id = str(uuid.uuid4())
    await request.app['redis'].set(taks_id, json.dumps({
        'container_id': container_id,
        'exercise': exercise_name}))
    return web.json_response({'id': taks_id})


async def get_result(request):
    taks_id = request.match_info['uuid']
    task_info = await request.app['redis'].get(taks_id)
    if task_info is None:
        raise web.HTTPNotFound()
    task_info = json.loads(task_info)
    runner = exercises.utils.Runner()
    if 'check_result' in task_info:
        result = task_info
    else:
        task_status = runner.get_results(task_info['container_id'])
        if task_status is not None:
            exit_code, stdout, stderr = task_status
            result = {
                'check_result': {
                    'exit_code': exit_code,
                    'stdout': stdout.decode(),
                    'stderr': stderr.decode()
                },
                'exercise': task_info['exercise']
            }
            await request.app['redis'].set(taks_id, json.dumps(result))
        else:
            result = {'error': {'message': 'Checking in progress'}}
    return web.json_response(result)
