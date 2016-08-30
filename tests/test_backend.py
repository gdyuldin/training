import json
import pytest
import uuid

import asyncio
import aiohttp
from hamcrest import (assert_that, has_entries, only_contains, instance_of,
    not_, has_key)


@pytest.yield_fixture
def create_app(event_loop, unused_tcp_port):
    app = handler = srv = client_session = None

    async def create():
        nonlocal app, handler, srv, client_session
        import training_backend.main
        app, _, _ = await training_backend.main.init(event_loop)
        handler = app.make_handler(debug=True, keep_alive_on=False)
        srv = await event_loop.create_server(handler, '127.0.0.1',
                                             unused_tcp_port)
        url = "http://127.0.0.1:{}".format(unused_tcp_port)
        client_session = aiohttp.ClientSession()
        return app, url, client_session

    yield create

    async def finish():
        await handler.finish_connections()
        await app.finish()
        await client_session.close()
        srv.close()
        await srv.wait_closed()

    event_loop.run_until_complete(finish())


@pytest.fixture
def correct_answer():
    import training_backend.main
    exercise_name = 'example_python'
    path = (training_backend.main.PROJ_ROOT.parent / 'exercises' /
            exercise_name / 'answer.py')
    with open(str(path), 'rt') as f:
        return exercise_name, json.dumps({'answer.py': f.read()})


@pytest.fixture
def long_answer():
    return 'example_python', json.dumps({'answer.py':
                                        'import time; time.sleep(2)'})


async def send_answer(client_session, base_url, correct_answer):
    exercise_name, answer_payload = correct_answer
    url = '{base_url}/exercises/{name}'.format(base_url=base_url,
                                               name=exercise_name)
    async with client_session.post(url,
                                   data=answer_payload) as response:
        content = await response.json()
        return content['id']


@pytest.mark.asyncio
async def test_exercises_list_status(create_app):
    app, url, client_session = await create_app()
    async with client_session.get('{}/exercises'.format(url)) as response:
        assert response.status == 200, await response.text()


@pytest.mark.asyncio
async def test_exercises_list_content(create_app):
    app, url, client_session = await create_app()
    async with client_session.get('{}/exercises'.format(url)) as response:
        content = await response.json()
        assert_that(content, has_entries(
            exercises=only_contains(
                has_entries(name=instance_of(str)))))


@pytest.mark.asyncio
async def test_not_exists_exercise_check_status(create_app):
    app, base_url, client_session = await create_app()
    exercise_name = 'not_exists'
    url = '{base_url}/exercises/{name}'.format(base_url=base_url,
                                               name=exercise_name)
    async with client_session.post(url, data={}) as response:
        assert response.status == 404, await response.text()


@pytest.mark.asyncio
async def test_exercise_check_status(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    url = '{base_url}/exercises/{name}'.format(base_url=base_url,
                                               name=exercise_name)
    async with client_session.post(url,
                                   data=answer_payload) as response:
        assert response.status == 200, await response.text()


@pytest.mark.asyncio
async def test_exercise_check_not_enough_files(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    url = '{base_url}/exercises/{name}'.format(base_url=base_url,
                                               name=exercise_name)
    async with client_session.post(url,
                                   data="{}") as response:
        assert response.status == 400, await response.text()


@pytest.mark.asyncio
async def test_exercise_check_answer(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    url = '{base_url}/exercises/{name}'.format(base_url=base_url,
                                               name=exercise_name)
    async with client_session.post(url,
                                   data=answer_payload) as response:
        content = await response.json()
        assert_that(content, has_entries(id=instance_of(str)))


@pytest.mark.asyncio
async def test_get_result_status(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    task_uuid = await send_answer(client_session, base_url, correct_answer)
    url = '{base_url}/results/{uuid}'.format(base_url=base_url,
                                             uuid=task_uuid)
    async with client_session.get(url) as response:
        assert response.status == 200, await response.text()


@pytest.mark.asyncio
async def test_get_not_exists_result_status(create_app):
    app, base_url, client_session = await create_app()
    task_uuid = str(uuid.uuid4())
    url = '{base_url}/results/{uuid}'.format(base_url=base_url,
                                             uuid=task_uuid)
    async with client_session.get(url) as response:
        assert response.status == 404, await response.text()


@pytest.mark.asyncio
async def test_get_result_answer(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    task_uuid = await send_answer(client_session, base_url, correct_answer)
    # TODO replace sleep with waiting
    await asyncio.sleep(2)
    url = '{base_url}/results/{uuid}'.format(base_url=base_url,
                                             uuid=task_uuid)
    async with client_session.get(url) as response:
        content = await response.json()
        assert_that(content, has_entries(
            check_result=has_entries(
                exit_code=instance_of(int),
                stdout=instance_of(str),
                stderr=instance_of(str)),
            exercise=exercise_name))


@pytest.mark.asyncio
async def test_get_result_twice(create_app, correct_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = correct_answer
    task_uuid = await send_answer(client_session, base_url, correct_answer)
    # TODO replace sleep with waiting
    await asyncio.sleep(2)
    url = '{base_url}/results/{uuid}'.format(base_url=base_url,
                                             uuid=task_uuid)
    async with client_session.get(url) as response:
        content = await response.json()
    async with client_session.get(url) as response:
        content2 = await response.json()
    assert content == content2


@pytest.mark.asyncio
async def test_get_long_result_answer(create_app, long_answer):
    app, base_url, client_session = await create_app()
    exercise_name, answer_payload = long_answer
    task_uuid = await send_answer(client_session, base_url, long_answer)
    url = '{base_url}/results/{uuid}'.format(base_url=base_url,
                                             uuid=task_uuid)
    async with client_session.get(url) as response:
        content = await response.json()
        assert_that(content, has_entries(
            error=has_entries(
                message='Checking in progress')))
    await asyncio.sleep(1)
    async with client_session.get(url) as response:
        content = await response.json()
        assert_that(content, not_(has_key('error')))
