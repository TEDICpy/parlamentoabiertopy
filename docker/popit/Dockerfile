FROM ubuntu:14.04
MAINTAINER Lupa <admin@tedic.org>

ENV DEBIAN_FRONTEND noninteractive
ENV DATA /data
ENV SRC /src
ENV POPIT /src/popit
ENV REPO https://github.com/mysociety/popit

# Sistem update and minimum needed packages
RUN apt-get update && apt-get upgrade -y \
	&& apt-get install -y python-software-properties wget apt-file software-properties-common

#---- PopIt specific package dependencies Repositories
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | \
    tee /etc/apt/sources.list.d/mongodb.list \
	&& apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add - \
	&& echo 'deb http://packages.elasticsearch.org/elasticsearch/0.90/debian stable main' | \
    tee /etc/apt/sources.list.d/elasticsearch.list

RUN add-apt-repository -y ppa:chris-lea/node.js \
	&& apt-get update

#-- Instalation of dependencies
RUN apt-get install -y python g++ make nodejs mongodb-org openjdk-6-jre elasticsearch \
    ruby1.9.1 ruby1.9.1-dev git graphicsmagick unzip

#-- Official  PopIt Repo
RUN mkdir -p $POPIT
WORKDIR $SRC
RUN git clone $REPO

#-- Local correction, Doesn't work without it
ADD print.scss $POPIT/public/sass/

#-- Build PopIt
WORKDIR $POPIT
RUN make node-modules \
	&& cp $POPIT/config/development.js-example $POPIT/config/development.js \
	&& gem install sass --version=3.2.14 --no-rdoc --no-ri \
	&& gem install compass --version=0.12.2 --no-rdoc --no-ri
RUN make css

#-- Config files for Parlamentoabierto.org.py
COPY init.sh $POPIT/
ADD default.js $POPIT/config/

RUN mkdir -p $DATA/db

#-- Run it!
CMD ["/src/popit/init.sh"]

