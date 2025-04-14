import os

from notifications_utils.gunicorn_defaults import set_gunicorn_defaults

set_gunicorn_defaults(globals())


workers = 4
timeout = int(os.getenv("HTTP_SERVE_TIMEOUT_SECONDS", 30))
