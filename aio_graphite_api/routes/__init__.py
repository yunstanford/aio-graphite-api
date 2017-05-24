from aiohttp import web
from ..templates import get_template
from .ping import add_ping_api
from .find import add_find_api
from .render import add_render_api
from aiohttp_transmute import (
    add_swagger_api_route,
    create_swagger_json_handler
)


async def handle(request):
    body = get_template("index.html").render(
        config=request.app["config"]
    ).encode("UTF-8")
    return web.Response(body=body, content_type='text/html')


def add_routes(app):
    # add apis
    add_ping_api(app)
    add_render_api(app)
    add_find_api(app)
    # route to swagger should be at the end, 
    # to ensure all routes are considered when
    # constructing the handler.
    # this will add:
    #   - a swagger.json definition
    #   - a static page that renders the swagger.json

    # app.router.add_route('GET', '/api/v1/swagger.json', create_swagger_json_handler(app))
    # add_swagger_api_route(app, "/api/v1/", "/api/v1/swagger.json")

    # add the generic root handler
    # make sure to add this at the end.
    resource = app.router.add_resource('/{route:.*}')
    resource.add_route('GET', handle)
