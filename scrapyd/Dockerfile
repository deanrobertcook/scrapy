# Assumes building from parent directory using:
# docker build -t quotes-scrapyd -f scrapyd/Dockerfile .

# Based heavily off of:
# https://github.com/cdrx/scrapyd-authenticated/blob/master/Dockerfile

# For some reason I've yet to understand, the scrapyd server
# needs to have all the dependencies of the spiders installed.
# I have no idea what the deploy step does then...

FROM ubuntu:18.04

# Example of variable to be used by the app
ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION:-latest}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT:-local}

# install Ubuntu packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get -y upgrade \
 && apt-get install --no-install-recommends -y \
    git net-tools \
    # python3 support
    python3 python3-pip python3-setuptools \
    # scrapy dependencies
    build-essential python3-dev \
    libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev \
    # nginx and htpasswd
    nginx apache2-utils \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

#Fixes a lot of issues further down the line
RUN pip3 install --upgrade pip

# install Chaperone
# (Unofficial repo due to: https://github.com/garywiz/chaperone/issues/24)
#RUN pip3 install chaperone \
RUN pip3 install git+https://github.com/necrophcodr/chaperone.git \
 && mkdir /etc/chaperone.d

# install Scrapyd and dependencies
ADD requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt \
 && pip3 freeze > /pip3-freeze.txt

# configure
ADD scrapyd/chaperone.conf /etc/chaperone.d/chaperone.conf
ADD scrapyd/nginx.conf /etc/nginx/sites-enabled/default
ADD scrapyd/scrapyd.conf /etc/scrapyd/scrapyd.conf

# expose
VOLUME /scrapyd
EXPOSE 6800

ENTRYPOINT ["/usr/local/bin/chaperone"]

