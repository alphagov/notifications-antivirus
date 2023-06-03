#!/usr/bin/env bash

set -eu

case "$@" in
  web)
    gunicorn --error-logfile - -c /home/vcap/app/gunicorn_config.py wsgi
    ;;
  worker)
    celery -A run_celery.notify_celery worker --loglevel=INFO --concurrency=4 --uid=`id -u celeryuser`
    ;;
  *)
    echo "Running custom command"
    $@
    ;;
esac

clamd