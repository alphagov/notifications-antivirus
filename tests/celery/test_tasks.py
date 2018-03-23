from app.celery.tasks import scan_file
from app.config import QueueNames


def test_test_scan_no_virus(notify_antivirus, mocker):
    filename = "RC-TEST-SCAN-LETTER.pdf"

    mocker.patch('app.celery.tasks._get_letter_pdf', return_value=b"test")
    mocker.patch('app.celery.tasks.clamav_scan', return_value=True)
    mock_send_task = mocker.patch('app.notify_celery.send_task')

    scan_file(filename)

    mock_send_task.assert_called_once_with(
        name='process-virus-scan-passed',
        kwargs={'filename': filename},
        queue=QueueNames.LETTERS,
    )


def test_test_scan_virus_detected(notify_antivirus, mocker):
    filename = "RC-TEST-SCAN-LETTER.pdf"

    mocker.patch('app.celery.tasks._get_letter_pdf', return_value=b"test")
    mocker.patch('app.celery.tasks.clamav_scan', return_value=False)
    mock_send_task = mocker.patch('app.notify_celery.send_task')

    scan_file(filename)

    mock_send_task.assert_called_once_with(
        name='process-virus-scan-failed',
        kwargs={'filename': filename},
        queue=QueueNames.LETTERS,
    )
