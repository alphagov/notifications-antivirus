import clamd
from flask import current_app
from notifications_utils.statsd_decorators import statsd


@statsd(namespace="antivirus")
def clamav_scan(stream):

    cd = clamd.ClamdUnixSocket()
    result = cd.instream(stream)

    if result['stream'][0] == 'FOUND':
        current_app.logger.error('VIRUS FOUND {}'.format(result['stream'][1]))
        return False
    else:
        return True
