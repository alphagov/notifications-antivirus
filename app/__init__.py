import os
import time

from flask import g, jsonify, request
from gds_metrics import GDSMetrics
from notifications_utils import request_helper
from notifications_utils.celery import NotifyCelery
from notifications_utils.clients.otel.otel_client import init_otel_app
from notifications_utils.clients.statsd.statsd_client import StatsdClient
from notifications_utils.logging import flask as utils_logging

from app.commands import setup_commands

notify_celery = NotifyCelery()
statsd_client = StatsdClient()
metrics = GDSMetrics()


def create_app(application):
    setup_commands(application)

    from app.config import Config, configs
    from app.views import main_blueprint

    notify_environment = os.environ["NOTIFY_ENVIRONMENT"]
    if notify_environment in configs:
        application.config.from_object(configs[notify_environment])
    else:
        application.config.from_object(Config)

    init_app(application)

    # Metrics intentionally high up to give the most accurate timing and reliability that the metric is recorded
    metrics.init_app(application)
    init_otel_app(application)

    statsd_client.init_app(application)
    utils_logging.init_app(application, statsd_client)
    request_helper.init_app(application)
    notify_celery.init_app(application)

    application.register_blueprint(main_blueprint)

    return application


def init_app(app):
    @app.before_request
    def record_request_details():
        g.start = time.monotonic()
        g.endpoint = request.endpoint

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
        return response

    @app.errorhandler(Exception)
    def exception(e):
        return jsonify(result="error", message=str(e))

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(result="error", message=str(e)), 404
