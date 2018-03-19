.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

PIP_ACCEL_CACHE ?= ${CURDIR}/cache/pip-accel
APP_VERSION_FILE = app/version.py

GIT_BRANCH ?= $(shell git symbolic-ref --short HEAD 2> /dev/null || echo "detached")
GIT_COMMIT ?= $(shell git rev-parse HEAD)


DOCKER_IMAGE = govuknotify/notifications-av
DOCKER_IMAGE_NAME = ${DOCKER_IMAGE}:master
DOCKER_BUILDER_IMAGE_NAME = govuk/notify-av-builder:master
DOCKER_TTY ?= $(if ${JENKINS_HOME},,t)

BUILD_TAG ?= notifications-av
BUILD_NUMBER ?= 0
DEPLOY_BUILD_NUMBER ?= ${BUILD_NUMBER}
BUILD_URL ?=

DOCKER_CONTAINER_PREFIX = ${USER}-${BUILD_TAG}

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: check-env-vars
check-env-vars: ## Check mandatory environment variables
	$(if ${STATSD_PREFIX},,$(error Must specify STATSD_PREFIX))
	$(if ${NOTIFICATION_QUEUE_PREFIX},,$(error Must specify NOTIFICATION_QUEUE_PREFIX))
	$(if ${NOTIFY_ENVIRONMENT},,$(error Must specify NOTIFY_ENVIRONMENT))
	$(if ${NOTIFICATION_QUEUE_PREFIX},,$(error Must specify NOTIFICATION_QUEUE_PREFIX))
	$(if ${FLASK_APP},,$(error Must specify FLASK_APP))
	$(if ${FLASK_DEBUG},,$(error Must specify FLASK_DEBUG))
	$(if ${WERKZEUG_DEBUG_PIN},,$(error Must specify WERKZEUG_DEBUG_PIN))
	$(if ${AWS_ACCESS_KEY_ID},,$(error Must specify AWS_ACCESS_KEY_ID))
	$(if ${AWS_SECRET_ACCESS_KEY},,$(error Must specify AWS_SECRET_ACCESS_KEY))


.PHONY: preview
preview: ## Set environment to preview
	$(eval export DEPLOY_ENV=preview)
	$(eval export DNS_NAME="notify.works")
	@true

.PHONY: staging
staging: ## Set environment to staging
	$(eval export DEPLOY_ENV=staging)
	$(eval export DNS_NAME="staging-notify.works")
	@true

.PHONY: production
production: ## Set environment to production
	$(eval export DEPLOY_ENV=production)
	$(eval export DNS_NAME="notifications.service.gov.uk")
	@true

.PHONY: _generate-version-file
_generate-version-file: ## Generates the app version file
	@echo -e "__travis_commit__ = \"${GIT_COMMIT}\"\n__time__ = \"${DATE}\"\n__travis_job_number__ = \"${BUILD_NUMBER}\"\n__travis_job_url__ = \"${BUILD_URL}\"" > ${APP_VERSION_FILE}

.PHONY: prepare-docker-build-image
prepare-docker-build-image: _generate-version-file ## Prepare the Docker builder image
	docker build -f docker/Dockerfile \
		--build-arg http_proxy="${http_proxy}" \
		--build-arg https_proxy="${https_proxy}" \
		-t ${DOCKER_IMAGE_NAME} \
		.

.PHONY: build-with-docker
build-with-docker: ;

define run_docker_container
	docker run -i${DOCKER_TTY} --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-${1}" \
		-e STATSD_PREFIX=${STATSD_PREFIX} \
		-e NOTIFICATION_QUEUE_PREFIX=${NOTIFICATION_QUEUE_PREFIX} \
		-e NOTIFY_ENVIRONMENT=${NOTIFY_ENVIRONMENT} \
		-e NOTIFICATION_QUEUE_PREFIX=${NOTIFICATION_QUEUE_PREFIX} \
		-e FLASK_APP=${FLASK_APP} \
		-e FLASK_DEBUG=${FLASK_DEBUG} \
		-e WERKZEUG_DEBUG_PIN=${WERKZEUG_DEBUG_PIN} \
		-e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		-e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		${DOCKER_IMAGE_NAME} \
		${2}
endef

.PHONY: run-with-docker
run-with-docker: prepare-docker-build-image ## Build inside a Docker container
	$(call run_docker_container,build)


.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true

.PHONY: clean
clean:
	rm -rf cache target venv .coverage build tests/.cache wheelhouse
