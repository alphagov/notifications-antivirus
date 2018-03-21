import os
import shutil

import pytest
from flask import current_app, Flask

from app import create_app


@pytest.fixture(scope='session')
def notify_antivirus():
    app = Flask('app')
    create_app(app)

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


@pytest.fixture(scope='function')
def client(notify_antivirus):
    with notify_antivirus.test_request_context(), notify_antivirus.test_client() as client:
        yield client
