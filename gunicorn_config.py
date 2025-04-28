from notifications_utils.gunicorn.defaults import set_gunicorn_defaults

set_gunicorn_defaults(globals())


workers = 4
