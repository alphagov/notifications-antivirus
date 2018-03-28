from io import BytesIO

import clamd

from app.clamav_client import clamav_scan


def test_scan_virus_found(notify_antivirus, mocker):

    found = {
        "stream": [
            "FOUND",
            "Eicar-Test-Signature"
        ]
    }

    mocker.patch('app.clamav_client.clamd.ClamdUnixSocket.instream', return_value=found)

    result = clamav_scan(BytesIO(clamd.EICAR))

    assert result is False


def test_scan_no_virus_found(notify_antivirus, mocker):

    found = {
        "stream": [
            "OK",
            None
        ]
    }

    mocker.patch('app.clamav_client.clamd.ClamdUnixSocket.instream', return_value=found)

    result = clamav_scan(BytesIO(clamd.EICAR))

    assert result
