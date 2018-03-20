from flask import current_app
from notifications_utils.statsd_decorators import statsd

from app import notify_celery
from app.config import QueueNames


@notify_celery.task(name="scan-file")
@statsd(namespace="tasks")
def scan_file(filename):
    current_app.logger.info('Scanning file: {}'.format(filename))

    # do the file scanning
    scan_passed = True

    if scan_passed:
        task_name = 'process-virus-scan-passed'
    else:
        task_name = 'process-virus-scan-failed'

    current_app.logger.info('Calling task: {} to process {} on API'.format(task_name, filename))
    notify_celery.send_task(
        name=task_name,
        kwargs={'filename': filename},
        queue=QueueNames.LETTERS,
    )
