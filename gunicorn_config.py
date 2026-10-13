import os

from notifications_utils.gunicorn.defaults import post_fork as utils_post_fork
from notifications_utils.gunicorn.defaults import set_gunicorn_defaults
from notifications_utils.semconv import set_service_instance_id
from opentelemetry.instrumentation import auto_instrumentation

set_gunicorn_defaults(globals())


# As we're using the gunicorn sync worker, we don't need to worry about the
# eventlet hub being left in a bad state post-fork. If we ever move this app to
# eventlet, we will need to use the
# notifications_utils.gunicorn.eventlet.OtelAwareEventletWorker worker class,
# and remove this post_fork hook.
def post_fork(server, worker):
    utils_post_fork(server, worker)
    if os.environ.get("OTEL_SERVICE_NAME") is not None:
        set_service_instance_id()
        auto_instrumentation.initialize()


workers = 4
