FROM ubuntu:14.04
MAINTAINER Lupa <admin@tedic.org>

ENV DEBIAN_FRONTEND noninteractive
ENV SRC /src
ENV POPIT /src/popit
ENV REPO https://github.com/TEDICpy/popit.git

# Sistem update and minimum needed packages
RUN apt-get update && apt-get upgrade -y \
	&& apt-get install -y python-software-properties wget apt-file software-properties-common

RUN add-apt-repository -y ppa:chris-lea/node.js \
	&& apt-get update

#-- Instalation of dependencies
RUN apt-get install -y python g++ make nodejs \
    ruby1.9.1 ruby1.9.1-dev git graphicsmagick unzip

#-- Official  PopIt Repo
RUN mkdir -p $POPIT
WORKDIR $SRC
RUN git clone $REPO

#-- Build PopIt
WORKDIR $POPIT
RUN make node-modules
ADD production.js $POPIT/config/
RUN gem install sass --version=3.2.14 --no-rdoc --no-ri \
	&& gem install compass --version=0.12.2 --no-rdoc --no-ri
RUN make css

#-- Config files for Parlamentoabierto.org.py
ADD init.sh $POPIT/
ADD default.js $POPIT/config/

#-- Run it!
CMD ["/src/popit/init.sh"]

