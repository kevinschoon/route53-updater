FROM python:3.4

MAINTAINER Kevin Schoon kevinschoon@gmail.com
COPY . /tmp/route53-updater
RUN pip3 install /tmp/route53-updater

CMD ['53Updater']
