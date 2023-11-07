from io import BytesIO

import boto3
import clamd
from botocore.exceptions import ClientError as BotoClientError
from flask import current_app

from app import notify_celery
from app.clamav_client import clamav_scan
from app.config import QueueNames


@notify_celery.task(bind=True, name="scan-file", max_retries=5, default_retry_delay=300)
def scan_file(self, filename):
    current_app.logger.info("Scanning file: %s", filename)

    try:
        if clamav_scan(BytesIO(_get_letter_pdf(filename))):
            task_name = "sanitise-letter"
        else:
            task_name = "process-virus-scan-failed"
            current_app.logger.info("VIRUS FOUND for file: %s", filename)

        current_app.logger.info("Calling task: %s to process %s on API", task_name, filename)
        notify_celery.send_task(
            name=task_name,
            kwargs={"filename": filename},
            queue=QueueNames.LETTERS,
        )
    except (clamd.ClamdError, BotoClientError) as e:
        try:
            current_app.logger.exception("Scanning error file: %s %s", filename, e)
            self.retry(queue=QueueNames.ANTIVIRUS)
        except self.MaxRetriesExceededError:
            current_app.logger.exception("MAX RETRY EXCEEDED: Task scan_file failed for file: %s", filename)

            notify_celery.send_task(
                name="process-virus-scan-error",
                kwargs={"filename": filename},
                queue=QueueNames.LETTERS,
            )


def _get_letter_pdf(filename):
    bucket_name = current_app.config["LETTERS_SCAN_BUCKET_NAME"]

    s3 = boto3.resource("s3")

    obj = s3.Object(bucket_name=bucket_name, key=filename)

    file_content = obj.get()["Body"].read()

    return file_content
