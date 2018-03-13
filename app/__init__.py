import os

from flask import Flask
from monotonic import monotonic

from app.celery.celery import NotifyCelery
from notifications_utils import logging
from notifications_utils.clients.statsd.statsd_client import StatsdClient
notify_celery = NotifyCelery()
statsd_client = StatsdClient()


def create_app():
    application = Flask(__name__)

    from app.config import configs

    notify_environment = os.environ['NOTIFY_ENVIRONMENT']

    application.config.from_object(configs[notify_environment])

    init_app(application)

    notify_celery.init_app(application)
    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)

    return application


def init_app(app):
    @app.before_request
    def record_request_details():
        g.start = monotonic()
        g.endpoint = request.endpoint

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    @app.errorhandler(Exception)
    def exception(e):
        return jsonify(result='error', message=str(e))

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(result='error', message=str(e)), 404
