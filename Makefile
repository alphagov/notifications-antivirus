.DEFAULT_GOAL := help
SHELL := /bin/bash
DATE = $(shell date +%Y-%m-%d:%H:%M:%S)

PIP_ACCEL_CACHE ?= ${CURDIR}/cache/pip-accel
APP_VERSION_FILE = app/version.py

GIT_BRANCH ?= $(shell git symbolic-ref --short HEAD 2> /dev/null || echo "detached")
GIT_COMMIT ?= $(shell git rev-parse HEAD)


DOCKER_IMAGE = govuknotify/notifications-ftp
DOCKER_IMAGE_NAME = ${DOCKER_IMAGE}:master
DOCKER_BUILDER_IMAGE_NAME = govuk/notify-ftp-builder:master
DOCKER_TTY ?= $(if ${JENKINS_HOME},,t)

BUILD_TAG ?= notifications-ftp-manual
BUILD_NUMBER ?= 0
DEPLOY_BUILD_NUMBER ?= ${BUILD_NUMBER}
BUILD_URL ?=

DOCKER_CONTAINER_PREFIX = ${USER}-${BUILD_TAG}

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: check-env-vars
check-env-vars: ## Check mandatory environment variables
	$(if ${DEPLOY_ENV},,$(error Must specify DEPLOY_ENV))
	$(if ${DNS_NAME},,$(error Must specify DNS_NAME))
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

.PHONY: test
test: ## run unit tests
	./scripts/run_tests.sh

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
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		${DOCKER_IMAGE_NAME} \
		${2}
endef

.PHONY: test-with-docker
test-with-docker: prepare-docker-build-image ## Run tests inside a Docker container
	$(call run_docker_container,test, make test)

.PHONY: coverage-with-docker
coverage-with-docker: ;

.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true

.PHONY: clean
clean:
	rm -rf cache target venv .coverage build tests/.cache wheelhouse

.PHONY: build-codedeploy-artifact
build-codedeploy-artifact: ## Build the deploy artifact for CodeDeploy
	rm -rf target
	mkdir -p target
	zip -y -q -r -x@deploy-exclude.lst target/notifications-ftp.zip ./

.PHONY: upload-codedeploy-artifact ## Upload the deploy artifact for CodeDeploy
upload-codedeploy-artifact: check-env-vars
	$(if ${DEPLOY_BUILD_NUMBER},,$(error Must specify DEPLOY_BUILD_NUMBER))
	aws s3 cp --region eu-west-1 --sse AES256 target/notifications-ftp.zip s3://${DNS_NAME}-codedeploy/notifications-ftp-${DEPLOY_BUILD_NUMBER}.zip

.PHONY: deploy
deploy: check-env-vars ## Trigger CodeDeploy for the api
	aws deploy create-deployment --application-name notify-ftp --deployment-config-name CodeDeployDefault.OneAtATime --deployment-group-name notify-ftp --s3-location bucket=${DNS_NAME}-codedeploy,key=notifications-ftp-${DEPLOY_BUILD_NUMBER}.zip,bundleType=zip --region eu-west-1
