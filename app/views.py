import clamd

from flask import Blueprint, current_app, jsonify, request
from flask_httpauth import HTTPTokenAuth

from app.clamav_client import clamav_scan

main_blueprint = Blueprint('main', __name__, url_prefix='')

auth = HTTPTokenAuth()


@main_blueprint.route('/_status')
def status():
    try:
        clamd.ClamdUnixSocket().ping()
    except Exception:
        return '', 500

    return 'ok', 200


@auth.verify_token
def verify_token(token):
    return token == current_app.config['ANTIVIRUS_API_KEY']


@main_blueprint.route('/scan', methods=['POST'])
@auth.login_required
def scan_document():
    if 'document' not in request.files:
        return jsonify(error='No document upload'), 400

    result = clamav_scan(request.files['document'])

    return jsonify(ok=result)
