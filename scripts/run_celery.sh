#!/bin/bash

set -e

clamd

celery -A run_celery.notify_celery worker --pidfile="/tmp/celery-celery.pid" --loglevel=INFO --concurrency=10 2> /dev/null
