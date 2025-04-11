bind = "0.0.0.0:10000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "api.main:app"
loglevel = "info"
accesslog = "-"
errorlog = "-" 