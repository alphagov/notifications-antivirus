FROM python:3.6-slim-jessie as parent

ENV CLAMAV_VERSION 0.101.4+dfsg-0+deb8u2

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        git \
        build-essential \
        clamav-daemon=${CLAMAV_VERSION}* \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 750 /var/run/clamav

RUN echo "TCPSocket 3310" >> /etc/clamav/clamd.conf

WORKDIR /home/vcap/app/

##### Test Image ##############################################################

FROM parent as test

COPY requirements.txt requirements.txt
COPY requirements_for_test.txt requirements_for_test.txt
RUN pip install -r requirements_for_test.txt

COPY . .

RUN wget -nv -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
    wget -nv -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
    wget -nv -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
    chown clamav:clamav /var/lib/clamav/*.cvd

ADD scripts/run_celery.sh /

CMD ["/run_celery.sh"]

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

ARG CI_NAME
ARG CI_BUILD_NUMBER
ARG CI_BUILD_URL
ENV CI_NAME=$CI_NAME
ENV CI_BUILD_NUMBER=$CI_BUILD_NUMBER
ENV CI_BUILD_URL=$CI_BUILD_URL

RUN wget -nv -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
    wget -nv -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
    wget -nv -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
    chown clamav:clamav /var/lib/clamav/*.cvd

RUN make _generate-version-file
