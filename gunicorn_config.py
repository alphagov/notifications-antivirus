import os
import sys
import traceback

workers = 4
errorlog = "/home/vcap/logs/gunicorn_error.log"
bind = "0.0.0.0:{}".format(os.getenv("PORT"))


def on_starting(server):
    server.log.info("Starting notifications-antivirus API")


def worker_abort(worker):
    worker.log.info("worker received ABORT %s", worker.pid)
    for _threadId, stack in sys._current_frames().items():
        worker.log.error("aborting worker\n%s", traceback.format_stack(stack))


def on_exit(server):
    server.log.info("Stopping notifications-antivirus API")


def worker_int(worker):
    worker.log.info("worker: received SIGINT %s", worker.pid)
