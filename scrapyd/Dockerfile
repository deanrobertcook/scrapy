# Assumes building from parent directory using:
# docker build -t quotes-scrapyd -f scrapyd/Dockerfile .

# Based heavily off of:
# https://github.com/cdrx/scrapyd-authenticated/blob/master/Dockerfile

# For some reason I've yet to understand, the scrapyd server
# needs to have all the dependencies of the spiders installed.
# I have no idea what the deploy step does then...

FROM python:3.8-slim

RUN apt-get update -qq \
    && apt-get -y upgrade \
    && apt-get install --no-install-recommends -y \ 
       git \
       nginx \ 
       apache2-utils \
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

# Example of variable to be used by the app
# Should go at the end to make best use of the build cache
ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION:-some_change}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT:-local}

