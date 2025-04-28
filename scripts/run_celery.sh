#!/bin/bash

set -e

clamd
CELERY_LOG_LEVEL=INFO celery -A run_celery.notify_celery worker
