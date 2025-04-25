.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%dT%H:%M:%S)

APP_VERSION_FILE = app/version.py

GIT_COMMIT ?= $(shell git rev-parse HEAD)

NOTIFY_CREDENTIALS ?= ~/.notify-credentials

DOCKER_IMAGE = ghcr.io/alphagov/notify/notifications-antivirus
DOCKER_IMAGE_TAG = $(shell git describe --always --dirty)
DOCKER_IMAGE_NAME = ${DOCKER_IMAGE}:${DOCKER_IMAGE_TAG}


.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ---- LOCAL FUNCTIONS ---- #
# should only call these from inside docker or this makefile

.PHONY: generate-version-file
generate-version-file:
	@echo -e "__git_commit__ = \"${GIT_COMMIT}\"\n__time__ = \"${DATE}\"" > ${APP_VERSION_FILE}

.PHONY: bootstrap
bootstrap: generate-version-file
	pip install -r requirements.txt
	python -c "from notifications_utils.version_tools import copy_config; copy_config()"
	pip install -r requirements_for_test.txt

.PHONY: freeze-requirements
freeze-requirements: ## create static requirements.txt
	pip install --upgrade pip-tools
	pip-compile requirements.in

.PHONY: bump-utils
bump-utils:  # Bump notifications-utils package to latest version
	python -c "from notifications_utils.version_tools import upgrade_version; upgrade_version()"

# ---- DOCKER COMMANDS ---- #

.PHONY: bootstrap-with-docker
bootstrap-with-docker: generate-version-file # Setup environment to run app commands
	docker build -f docker/Dockerfile --target test -t notifications-antivirus --build-arg CLAMAV_USE_MIRROR=false .

.PHONY: run-celery-with-docker
run-celery-with-docker: ## Run celery in Docker container
	$(if ${NOTIFICATION_QUEUE_PREFIX},,$(error Must specify NOTIFICATION_QUEUE_PREFIX))
	./scripts/run_with_docker.sh ./scripts/run_celery.sh

.PHONY: run-flask-with-docker
run-flask-with-docker: ## Run flask in Docker container
	export DOCKER_ARGS="-p 127.0.0.1:6016:6016" && ./scripts/run_with_docker.sh ./scripts/run_app.sh

.PHONY: test
test: ## Run tests (used by Concourse)
	ruff check .
	black --check .
	PYTHONPATH=. pytest

.PHONY: test-with-docker
test-with-docker: ## Run tests in Docker container
	./scripts/run_with_docker.sh make test

.PHONY: upload-to-docker-registry
upload-to-docker-registry: ## Upload the current version of the docker image to Docker registry
	$(if ${DOCKER_USER_NAME},,$(error Must specify DOCKER_USER_NAME))
	$(if ${CF_DOCKER_PASSWORD},,$(error Must specify CF_DOCKER_PASSWORD))
	@docker login ${DOCKER_IMAGE} -u ${DOCKER_USER_NAME} -p ${CF_DOCKER_PASSWORD}
	docker buildx build --platform linux/amd64 --push -f docker/Dockerfile -t ${DOCKER_IMAGE_NAME} .
