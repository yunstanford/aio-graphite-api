import aiohttp_transmute


@aiohttp_transmute.describe(methods="GET", paths="/ping")
async def ping():
	return {}


def add_ping_api(app):
	app.router.add_transmute_route(ping)
