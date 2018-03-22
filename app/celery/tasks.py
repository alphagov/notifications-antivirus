from io import BytesIO

import boto3
from flask import current_app
from notifications_utils.statsd_decorators import statsd

from app import notify_celery
from app.clamav_client import clamav_scan
from app.config import QueueNames


@notify_celery.task(name="scan-file")
@statsd(namespace="antivirus")
def scan_file(filename):
    current_app.logger.info('Scanning file: {}'.format(filename))

    if clamav_scan(BytesIO(_get_letter_pdf(filename))):
        task_name = 'process-virus-scan-passed'
    else:
        task_name = 'process-virus-scan-failed'

    current_app.logger.info('Calling task: {} to process {} on API'.format(task_name, filename))
    notify_celery.send_task(
        name=task_name,
        kwargs={'filename': filename},
        queue=QueueNames.LETTERS,
    )


def _get_letter_pdf(filename):

    bucket_name = current_app.config['LETTERS_SCAN_BUCKET_NAME']

    s3 = boto3.resource('s3')

    obj = s3.Object(
        bucket_name=bucket_name,
        key=filename
    )

    file_content = obj.get()["Body"].read()

    return file_content
