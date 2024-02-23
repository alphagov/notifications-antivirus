ARG BASE_IMAGE=ghcr.io/alphagov/notify/notifications-antivirus:base
FROM python:3.11-slim-bookworm as base

ENV CLAMAV_MIRROR_URL https://s3.eu-west-1.amazonaws.com/notifications.service.gov.uk-clamav-database-mirror/clam
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Use clamav database from private mirror. Disable with: --build-arg CLAMAV_USE_MIRROR=false for local builds
ARG CLAMAV_USE_MIRROR=true

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
        git \
        make \
        clamav-daemon \
        clamav-freshclam \
        libcurl4 \
        curl \
        && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav && \
    chown clamav:clamav /usr/sbin/clamd && \
    chmod u+s /usr/sbin/clamd

RUN echo "TCPSocket 3310" >> /etc/clamav/clamd.conf
RUN if [ "$CLAMAV_USE_MIRROR" = "true" ] ; then echo "PrivateMirror ${CLAMAV_MIRROR_URL}" >> /etc/clamav/freshclam.conf ; fi

# make sure we exit with status 1 if we've been rate limited. otherwise we risk
# deploying this image with no definitions, which will fail to detect viruses!
# tee /dev/stderr means we can still see the full output from freshclam.
RUN freshclam --stdout | tee /dev/stderr > freshclam.out
RUN ! grep "received error code 429" freshclam.out
RUN rm freshclam.out

WORKDIR /home/vcap/app/

##### Python Build Image #####################################################
FROM ${BASE_IMAGE} AS python_build

RUN echo "Install OS dependencies for python app requirements" && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        libcurl4-openssl-dev \
        libssl-dev && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

COPY requirements.txt .

RUN echo "Installing python requirements" && \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install -r requirements.txt

COPY . .
RUN make generate-version-file  # This file gets copied across

##### Production Image #######################################################
FROM ${BASE_IMAGE} as production

RUN groupadd -r notify && \
    useradd -r -g notify -ms /bin/bash notify && \
    usermod -a -G clamav notify && \
    chown -R notify:notify /home/vcap
USER notify

RUN mkdir /home/vcap/logs

COPY --from=python_build --chown=root:root /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY --chown=notify:notify app app
COPY --chown=notify:notify scripts scripts
COPY --chown=notify:notify application.py run_celery.py gunicorn_config.py Makefile ./
COPY --from=python_build --chown=notify:notify /home/vcap/app/app/version.py app/version.py

##### Test Image ##############################################################
FROM production as test

USER root
RUN chown -R notify:notify /opt/venv
RUN echo "Install OS dependencies for test build" && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    git \
    libcurl4-openssl-dev \
    libssl-dev && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*
USER notify

# Make sure the app/ directory is there so that "make bootstrap" can create app/version.py
RUN mkdir -p app

# Install dev/test requirements
COPY --chown=notify:notify requirements.txt requirements_for_test.txt ./
RUN make bootstrap

COPY --chown=notify:notify . .
