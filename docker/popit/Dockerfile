FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
ENV data /data
ENV src /src
ENV popit $src/popit
ENV repo https://github.com/mysociety/popit 

# Sistem update and minimum needed packages
RUN apt-get update \
	&& apt-get upgrade -y
	&& apt-get install -y python-software-properties wget apt-file software-properties-common

#---- PopIt specific package dependencies Repositories
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | \
    sudo tee /etc/apt/sources.list.d/mongodb.list

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/0.90/debian stable main' | \
    sudo tee /etc/apt/sources.list.d/elasticsearch.list

RUN add-apt-repository ppa:chris-lea/node.js \
	&& apt-get update

#-- Instalation of dependencies
RUN apt-get install -y python g++ make nodejs mongodb-org openjdk-6-jre elasticsearch \
    ruby1.9.1 ruby1.9.1-dev  git graphicsmagick unzip sendmail

#-- Folder creation
RUN mkdir -p $src
RUN mkdir -p $data/db

#-- Official  PopIt Repo
WORKDIR $src
RUN git clone $repo

#-- Local correction, Doesn't work without it
ADD print.scss $popit/public/sass/

#-- Build PopIt
WORKDIR $popit
RUN make node-modules \
	&& cp config/development.js-example config/development.js \
	&& gem install sass --version=3.2.14 --no-rdoc --no-ri
	&& gem install compass --version=0.12.2 --no-rdoc --no-ri
RUN make css

#-- Config files for Parlamentoabierto.org.py
ADD init.sh $popit/
ADD default.js $popit/config/

#-- Run it!
CMD sh $popit/init.sh
