# carbon-cache api

import aiohttp_transmute


@aiohttp_transmute.describe(methods="GET",
                paths="/cache/")
async def query_carbon_cache(request, metric):
	if not metric:
		return {}
	datapoints = await request.app["conn"].query(metric)
	return {
		"target": metric,
		"datapoints": datapoints
	}


def add_carbon_cache_api(app):
	app.router.add_transmute_route(query_carbon_cache)
