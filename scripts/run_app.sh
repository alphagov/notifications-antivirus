#!/bin/bash

set -e

clamd &
# sleep for because clamav needs to start and maybe download the virus database
sleep 15

flask run -p 6016 -h 0.0.0.0
