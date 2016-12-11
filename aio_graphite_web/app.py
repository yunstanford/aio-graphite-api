import os
import aiohttp
from aiohttp import web
from aiohttp_transmute import TransmuteUrlDispatcher
from .routes import add_routes


async def create_app(loop, config, **kwargs):
    # Application: synonym for web-server. 
    # loop: event loop used for processing HTTP requests.
    # router: dispatches url to request handler.
    # For more info http://aiohttp.readthedocs.io/en/stable/web_reference.html#application-and-router
    app = web.Application(
        loop=loop,
        # a custom router is needed to help find the transmute functions.
        # To allow aiohttp-transmute to autodocument your library, 
        # you must use the TransmuteUrlDispatcher as your application’s router
        router=TransmuteUrlDispatcher(),
    )

    # register supported urls in router
    add_routes(app)

    # Application is a dict-like object, you can use it to share data globally 
    # for later access from a handler via the Request.app property.
    # http://aiohttp.readthedocs.io/en/stable/web.html#data-sharing
    app["config"] = config
    app.update(**kwargs)

    # Any Initializing Work should be here.
    # For example, initialize carbon conn pool
    await init_app(app, config)

    return app


async def init_app(app, config):
    if "conn" not in app:
        app["conn"] = init_conn_pool(config)
