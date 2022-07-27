FROM python:3.9.9-slim-bullseye as parent

ENV CLAMAV_MIRROR_URL https://s3.eu-west-1.amazonaws.com/notifications.service.gov.uk-clamav-database-mirror/clam

# Use clamav database from private mirror. Disable with: --build-arg CLAMAV_USE_MIRROR=false for local builds
ARG CLAMAV_USE_MIRROR=true

RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        git \
        build-essential \
        clamav-daemon \
        clamav-freshclam \
        libcurl4-openssl-dev \
        libssl-dev \
    && \
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

COPY requirements.txt .
RUN pip install -r requirements.txt

##### Test Image ##############################################################

FROM ghcr.io/alphagov/notify/notifications-antivirus:base as test

COPY . .

RUN make bootstrap

##### Production Image #######################################################

FROM ghcr.io/alphagov/notify/notifications-antivirus:base as production

RUN useradd -ms /bin/bash celeryuser && usermod -a -G clamav celeryuser

COPY app app
COPY application.py .
COPY run_celery.py .
COPY gunicorn_config.py .
COPY Makefile .

COPY scripts/run_app.sh scripts/run_app.sh
COPY scripts/run_celery.sh scripts/run_celery.sh
COPY scripts/run_app_paas.sh scripts/run_app_paas.sh

RUN make generate-version-file
