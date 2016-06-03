FROM alpine:edge
MAINTAINER Wonderfalll <wonderfall@schrodinger.io>

ENV UID=991 GID=991 TZ=Europe/Berlin

RUN echo "@commuedge http://nl.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
 && apk -U add \
    python3 \
    python3-dev \
    build-base \
    openssl \
    ca-certificates \
    linux-headers \
    tini@commuedge \
    su-exec \
 && cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py \
 && pip3 install --no-cache \
    speedtest-cli \
    psutil \
    twython \
    apscheduler \
 && apk del \
    python3-dev \
    build-base \
    openssl \
    ca-certificates \
    linux-headers \
 && rm -f /var/cache/apk/* \
 && mkdir /opt

COPY run.sh /usr/local/bin/run.sh
COPY twitbot.py /opt/twitbot.py

RUN chmod +x /usr/local/bin/run.sh

CMD ["/sbin/tini","--","run.sh"]
