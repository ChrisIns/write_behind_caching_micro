FROM ubuntu

RUN apt-get update

RUN apt install memcached -y

RUN apt install libmemcached-tools -y

EXPOSE 11211


CMD /usr/bin/memcached -m 64 -p 11211 -u memcache

