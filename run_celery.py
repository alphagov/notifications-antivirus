#!/usr/bin/env python

from app.performance import init_performance_monitoring

init_performance_monitoring()

from flask import Flask  # noqa

# notify_celery is referenced from manifest_delivery_base.yml, and cannot be removed
from app import notify_celery, create_app  # noqa


application = Flask('antivirus')
create_app(application)
application.app_context().push()
