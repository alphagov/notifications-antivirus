#!/bin/bash
case $NOTIFY_APP_NAME in
  notify-antivirus-api)
    unset GUNICORN_CMD_ARGS
    ./scripts/run_app_paas.sh gunicorn -c gunicorn_config.py application
    ;;
  notify-antivirus)
    ./scripts/run_app_paas.sh celery -A run_celery.notify_celery worker --loglevel=INFO --concurrency=4 --uid=`id -u celeryuser` 2> /dev/null
    ;;
  *)
    echo "Unknown notify_app_name $NOTIFY_APP_NAME"
    exit 1
    ;;
esac
