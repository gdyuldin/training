import asyncio
import logging
import pathlib

from aiohttp import web
import asyncio_redis

from .routes import setup_routes
from .utils import load_config

PROJ_ROOT = pathlib.Path(__file__).parent

async def init_redis(conf):
    connection = await asyncio_redis.Pool.create(
        host=conf['redis']['host'],
        port=int(conf['redis']['port']),
        poolsize=int(conf['redis']['poolsize']))
    return connection

async def close_redis(app):
    app['redis'].close()


async def init(loop, debug=False):
    # load config from yaml file in current dir
    conf = load_config(str(PROJ_ROOT / 'config' / 'settings.yaml'))

    # setup application and extensions
    app = web.Application(loop=loop, debug=debug)

    # setup redis
    redis = await init_redis(conf)
    app['redis'] = redis

    app.on_cleanup.append(close_redis)

    # setup redis
    redis = await init_redis(conf)
    app['redis'] = redis

    app.on_cleanup.append(close_redis)

    # setup views and routes
    setup_routes(app)

    host, port = conf['host'], conf['port']

    return app, host, port


def main():
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()
