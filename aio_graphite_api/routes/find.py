# graphite web find api
import aiohttp_transmute


@aiohttp_transmute.describe(methods="GET", paths="/metrics/find/")
async def find(request, query, from=None, util=None):
	return {}


def add_find_api(app):
	app.router.add_transmute_route(find)
