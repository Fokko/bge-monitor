FROM ubuntu:latest

ADD . /app/

WORKDIR /app/

RUN apt-get update \
 && apt-get install -y python-pip python-dev nginx supervisor build-essential \
 && pip install --upgrade pip \
 && pip install uwsgi \
 && apt-get clean

RUN pip install -r requirements.txt

ADD nginx/default.conf /etc/nginx/conf.d/default.conf
ADD nginx/nginx.conf /etc/nginx/nginx.conf
#ADD nginx/htpasswd /etc/nginx/conf/htpasswd

CMD ["/usr/bin/supervisord", "-c", "/app/supervisord/supervisord.conf"]
