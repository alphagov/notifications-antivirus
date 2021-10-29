FROM python:3.9-slim as parent

ENV CLAMAV_VERSION 0.103.3

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        git \
        build-essential \
        clamav-daemon=${CLAMAV_VERSION}* \
        clamav-freshclam=${CLAMAV_VERSION}* \
        libcurl4-openssl-dev \
        libssl-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

RUN echo "TCPSocket 3310" >> /etc/clamav/clamd.conf

RUN freshclam

WORKDIR /home/vcap/app/

##### Test Image ##############################################################

FROM parent as test

COPY . .

RUN make bootstrap

##### Production Image #######################################################

FROM parent as production

RUN useradd -ms /bin/bash celeryuser && usermod -a -G clamav celeryuser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY application.py .
COPY run_celery.py .
COPY gunicorn_config.py .
COPY Makefile .

COPY scripts/run_app.sh scripts/run_app.sh
COPY scripts/run_celery.sh scripts/run_celery.sh
COPY scripts/run_app_paas.sh scripts/run_app_paas.sh

RUN make generate-version-file
