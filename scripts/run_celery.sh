#!/bin/bash

set -e

clamd
celery -A run_celery.notify_celery worker
