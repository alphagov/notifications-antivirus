from flask import current_app

from app import notify_celery
from app.config import QueueNames
from app.statsd_decorators import statsd


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

    # filename looks like '2018-01-13/NOTIFY.ABCDEF1234567890.D.2.C.C.20180113120000.PDF'
    reference = filename.split('.')[1]
    current_app.logger.info('Calling task: {} to process {} on API'.format(task_name, reference))
    notify_celery.send_task(
        name=task_name,
        kwargs={'reference': reference},
        queue=QueueNames.LETTERS,
    )
