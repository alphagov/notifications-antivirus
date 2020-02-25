from botocore.exceptions import ClientError as BotoClientError
from celery.exceptions import MaxRetriesExceededError
from clamd import ClamdError

from app.celery.tasks import scan_file
from app.config import QueueNames

TEST_FILENAME = "EXAMPLE-SCAN-LETTER.pdf"


def test_scan_no_virus(notify_antivirus, mocker):
    mocker.patch('app.celery.tasks._get_letter_pdf', return_value=b"test")
    mocker.patch('app.celery.tasks.clamav_scan', return_value=True)
    mock_send_task = mocker.patch('app.notify_celery.send_task')

    scan_file(TEST_FILENAME)

    mock_send_task.assert_called_once_with(
        name='sanitise-letter',
        kwargs={'filename': TEST_FILENAME},
        queue=QueueNames.LETTERS,
    )


def test_scan_virus_detected(notify_antivirus, mocker):

    mocker.patch('app.celery.tasks._get_letter_pdf', return_value=b"test")
    mocker.patch('app.celery.tasks.clamav_scan', return_value=False)
    mock_send_task = mocker.patch('app.notify_celery.send_task')

    scan_file(TEST_FILENAME)

    mock_send_task.assert_called_once_with(
        name='process-virus-scan-failed',
        kwargs={'filename': TEST_FILENAME},
        queue=QueueNames.LETTERS,
    )


def test_scan_virus_clamav_error(notify_antivirus, mocker):

    mocker.patch('app.celery.tasks._get_letter_pdf', return_value=b"test")
    mocker.patch('app.clamav_client.clamav_scan', side_effect=ClamdError())
    mock_retry = mocker.patch('app.celery.tasks.scan_file.retry')

    scan_file(TEST_FILENAME)

    assert mock_retry.called


def test_scan_virus_boto_error(notify_antivirus, mocker):

    mocker.patch('app.celery.tasks._get_letter_pdf', side_effect=BotoClientError({}, "S3 Error"))
    mock_retry = mocker.patch('app.celery.tasks.scan_file.retry')

    scan_file(TEST_FILENAME)

    assert mock_retry.called


def test_scan_virus_max_retries(notify_antivirus, mocker):

    mocker.patch('app.celery.tasks._get_letter_pdf', side_effect=BotoClientError({}, "S3 Error"))
    mocker.patch('app.celery.tasks.scan_file.retry', side_effect=MaxRetriesExceededError)
    mock_send_task = mocker.patch('app.notify_celery.send_task')

    scan_file(TEST_FILENAME)

    mock_send_task.assert_called_once_with(
        name='process-virus-scan-error',
        kwargs={'filename': TEST_FILENAME},
        queue=QueueNames.LETTERS,
    )
