#!/bin/bash
DOCKER_IMAGE_NAME=notifications-antivirus

source environment.sh

docker run -it --rm \
  -e NOTIFY_ENVIRONMENT=development \
  -e FLASK_APP=application.py \
  -e FLASK_ENV=development \
  -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-$(aws configure get aws_access_key_id)} \
  -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-$(aws configure get aws_secret_access_key)} \
  -e NOTIFY_LOG_PATH=/var/log/notify/antivirus \
  -e NOTIFICATION_QUEUE_PREFIX=${NOTIFICATION_QUEUE_PREFIX} \
  -v $(pwd):/home/vcap/app \
  ${DOCKER_ARGS} \
  ${DOCKER_IMAGE_NAME} \
  ${@}
