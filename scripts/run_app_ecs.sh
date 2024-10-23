#!/bin/bash

set -e -o pipefail

TERMINATE_TIMEOUT=10

function on_exit {
  echo "Terminating application process with pid ${APP_PID}"
  kill ${APP_PID} || true
  n=0
  while (kill -0 ${APP_PID} 2&>/dev/null); do
    echo "Application is still running.."
    sleep 1
    let n=n+1
    if [ "$n" -ge "$TERMINATE_TIMEOUT" ]; then
      echo "Timeout reached, killing process with pid ${APP_PID}"
      kill -9 ${APP_PID} || true
      break
    fi
  done
  echo "Application process terminated, waiting 10 seconds"
  sleep 10
  echo "Terminating remaining subprocesses.."
  kill 0
}

function start_clamd {
  clamd
}

function start_application {
  exec "$@" &
  APP_PID=`jobs -p`
  echo "Application process pid: ${APP_PID}"
}

function run {
  while true; do
    kill -0 ${APP_PID} 2&>/dev/null || break
    python -c "import clamd, sys; clamd.ClamdUnixSocket().ping()" || break
    sleep 1
  done
}

echo "Run script pid: $$"

trap "on_exit" EXIT

cat >> /etc/clamav/clamd.conf <<EOF
MaxScanTime ${CLAMD_MAX_SCAN_TIME_MS:-50}
EOF

start_clamd

# The application has to start first!
start_application "$@"

run
