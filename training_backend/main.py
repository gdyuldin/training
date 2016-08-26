import asyncio
import logging
import pathlib


from aiohttp import web

from .routes import setup_routes
from .utils import load_config

PROJ_ROOT = pathlib.Path(__file__).parent


async def init(loop):
    # load config from yaml file in current dir
    conf = load_config(str(PROJ_ROOT / 'config' / 'settings.yaml'))

    # setup application and extensions
    app = web.Application(loop=loop)

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
