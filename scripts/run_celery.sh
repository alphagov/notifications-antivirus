#!/bin/bash

set -e

freshclam -d &
clamd &
# sleep for because clamav needs to start and maybe download the virus database
sleep 15; celery -A run_celery.notify_celery worker --pidfile="/tmp/celery-celery.pid" --loglevel=INFO --concurrency=10
