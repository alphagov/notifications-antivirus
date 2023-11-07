import clamd
from flask import current_app


def clamav_scan(stream):
    cd = clamd.ClamdUnixSocket()
    result = cd.instream(stream)

    if result["stream"][0] == "FOUND":
        current_app.logger.info("VIRUS FOUND %s", result["stream"][1])
        return False
    else:
        return True
