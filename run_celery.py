#!/usr/bin/env python
from app import notify_celery, create_app  # noqa: notify_celery required to get celery running

application = create_app()
application.app_context().push()
