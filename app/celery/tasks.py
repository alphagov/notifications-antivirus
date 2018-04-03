from io import BytesIO

import boto3
import clamd
from boto.exception import BotoClientError
from flask import current_app
from notifications_utils.statsd_decorators import statsd

from app import notify_celery
from app.clamav_client import clamav_scan
from app.config import QueueNames


@notify_celery.task(bind=True, name="scan-file", max_retries=5, default_retry_delay=300)
@statsd(namespace="antivirus")
def scan_file(self, filename):
    current_app.logger.info('Scanning file: {}'.format(filename))

    try:

        if clamav_scan(BytesIO(_get_letter_pdf(filename))):
            task_name = 'process-virus-scan-passed'
        else:
            task_name = 'process-virus-scan-failed'
            current_app.logger.error('VIRUS FOUND for file: {}'.format(filename))

        current_app.logger.info('Calling task: {} to process {} on API'.format(task_name, filename))
        notify_celery.send_task(
            name=task_name,
            kwargs={'filename': filename},
            queue=QueueNames.LETTERS,
        )
    except (clamd.ClamdError, BotoClientError) as e:
        try:
            current_app.logger.exception("Scanning error file: {} {}".format(filename, e))
            self.retry(queue=QueueNames.ANTIVIRUS)
        except self.MaxRetriesExceededError:
            current_app.logger.exception("MAX RETRY EXCEEDED: Task scan_file failed for file: {}".format(filename))

            notify_celery.send_task(
                name='process-virus-scan-error',
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
