# render api

import aiohttp_transmute


@aiohttp_transmute.describe(methods="GET",
                paths="/render/")
async def render(request, target=None,
				 from=None, until=None):
	
	


def add_render_api(app):
	app.router.add_transmute_route(render)
