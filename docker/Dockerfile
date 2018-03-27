FROM python:3.6-slim

ENV CLAMAV_VERSION 0.99

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        git \
        build-essential \
        clamav-daemon=${CLAMAV_VERSION}* \
        clamav-freshclam=${CLAMAV_VERSION}* \
        libclamunrar7 \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
    wget -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
    wget -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
    chown clamav:clamav /var/lib/clamav/*.cvd

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

RUN sed -i 's/^Foreground .*$/Foreground true/g' /etc/clamav/clamd.conf && \
    echo "TCPSocket 3310" >> /etc/clamav/clamd.conf && \
    sed -i 's/^Foreground .*$/Foreground true/g' /etc/clamav/freshclam.conf

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY application.py .
COPY run_celery.py .
COPY Makefile .


COPY scripts/run_celery.sh scripts/run_celery.sh

ARG CI_NAME
ARG CI_BUILD_NUMBER
ARG CI_BUILD_URL
ENV CI_NAME=$CI_NAME
ENV CI_BUILD_NUMBER=$CI_BUILD_NUMBER
ENV CI_BUILD_URL=$CI_BUILD_URL

RUN make _generate-version-file
