import os
from notifications_utils.gunicorn.defaults import set_gunicorn_defaults
from notifications_utils.semconv import set_service_instance_id
from opentelemetry.instrumentation import auto_instrumentation

set_gunicorn_defaults(globals())


workers = 4

if os.environ.get("OTEL_SERVICE_NAME") is not None:

    def post_fork(server, worker):
        set_service_instance_id()
        auto_instrumentation.initialize()
