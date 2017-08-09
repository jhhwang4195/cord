FROM haproxy:1.7

RUN apt-get update \
    && apt-get install -y vim net-tools hatop

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
