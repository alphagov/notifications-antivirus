#!/bin/bash

set -e

clamd

flask run -p 6016 -h 0.0.0.0
