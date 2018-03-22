import pytest
from flask import Flask

from app import create_app


@pytest.fixture(scope='session')
def notify_antivirus():
    application = Flask('app')

    create_app(application)

    ctx = application.app_context()
    ctx.push()

    yield application

    ctx.pop()


@pytest.fixture(scope='function')
def client(notify_antivirus):
    with notify_antivirus.test_request_context(), notify_antivirus.test_client() as client:
        yield client
