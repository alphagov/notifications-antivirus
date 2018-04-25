from flask import Blueprint, jsonify, request

from app.clamav_client import clamav_scan

main_blueprint = Blueprint('main', __name__, url_prefix='')


@main_blueprint.route('/scan', methods=['POST'])
def scan_document():
    if 'document' not in request.files:
        return jsonify(error='No document upload'), 400

    result = clamav_scan(request.files['document'])

    return jsonify(ok=result)
