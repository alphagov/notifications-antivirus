import os

from kombu import Exchange, Queue


class QueueNames(object):
    LETTERS = "letter-tasks"
    ANTIVIRUS = "antivirus-tasks"


class Config(object):
    STATSD_ENABLED = True
    STATSD_HOST = os.getenv("STATSD_HOST")
    STATSD_PORT = 8125

    NOTIFICATION_QUEUE_PREFIX = os.getenv("NOTIFICATION_QUEUE_PREFIX")

    # Logging
    DEBUG = False
    LOGGING_STDOUT_JSON = os.getenv("LOGGING_STDOUT_JSON") == "1"

    ###########################
    # Default config values ###
    ###########################

    NOTIFY_APP_NAME = "antivirus"
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
    NOTIFY_LOG_PATH = os.getenv("NOTIFY_LOG_PATH")

    ANTIVIRUS_API_KEY = os.getenv("ANTIVIRUS_API_KEY")

    CELERY = {
        "broker_url": "https://sqs.eu-west-1.amazonaws.com",
        "broker_transport": "sqs",
        "broker_transport_options": {
            "region": AWS_REGION,
            "visibility_timeout": 310,
            "queue_name_prefix": NOTIFICATION_QUEUE_PREFIX,
            "is_secure": True,
            "wait_time_seconds": 20,  # enable long polling, with a wait time of 20 seconds
        },
        "timezone": "Europe/London",
        "imports": ["app.celery.tasks"],
        "task_queues": [Queue(QueueNames.ANTIVIRUS, Exchange("default"), routing_key=QueueNames.ANTIVIRUS)],
    }

    LETTERS_SCAN_BUCKET_NAME = None


######################
# Config overrides ###
######################


class Development(Config):
    SERVER_NAME = os.getenv("SERVER_NAME")

    NOTIFICATION_QUEUE_PREFIX = "development"
    DEBUG = True
    STATSD_ENABLED = False

    ANTIVIRUS_API_KEY = "test-key"

    LETTERS_SCAN_BUCKET_NAME = "development-letters-scan"


class Test(Config):
    DEBUG = True
    STATSD_HOST = "localhost"
    STATSD_PORT = 1000

    ANTIVIRUS_API_KEY = "test-key"

    LETTERS_SCAN_BUCKET_NAME = "test-letters-pdf"


class Preview(Config):
    LETTERS_SCAN_BUCKET_NAME = "preview-letters-scan"


class Staging(Config):
    LETTERS_SCAN_BUCKET_NAME = "staging-letters-scan"


class Production(Config):
    LETTERS_SCAN_BUCKET_NAME = "production-letters-scan"


configs = {
    "development": Development,
    "test": Test,
    "preview": Preview,
    "staging": Staging,
    "production": Production,
}
