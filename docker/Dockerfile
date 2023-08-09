ARG BASE_IMAGE=ghcr.io/alphagov/notify/notifications-antivirus:base
FROM python:3.9.9-slim-bullseye as base

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
        libcurl4 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

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
        curl \
        libssl-dev && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* /tmp/*

COPY requirements.txt .

RUN echo "Installing python requirements" && \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install -r requirements.txt

##### Production Image #######################################################
FROM ${BASE_IMAGE} as production

RUN groupadd -r notify && \
    useradd -r -g notify -ms /bin/bash notify && \
    usermod -a -G clamav notify && \
    chown -R notify:notify /home/vcap
USER notify

COPY --from=python_build --chown=root:root /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY app app
COPY scripts scripts
COPY application.py run_celery.py gunicorn_config.py Makefile .

RUN make generate-version-file

##### Test Image ##############################################################
FROM production as test

COPY requirements.txt requirements.in ./

RUN make bootstrap

COPY . .
