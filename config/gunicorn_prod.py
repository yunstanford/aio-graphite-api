workers = 4
bind = "0.0.0.0:8080"
max_requests = 10000
worker_class = "aiohttp.worker.GunicornWebWorker"
