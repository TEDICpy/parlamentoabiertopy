FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
ENV data /data
ENV src /src

# Sistem update and minimum needed packages
RUN touch /pop-it
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties wget apt-file software-properties-common

#---- PopIt specific package dependencies Repositories
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/0.90/debian stable main' | sudo tee /etc/apt/sources.list.d/elasticsearch.list
RUN add-apt-repository ppa:chris-lea/node.js
RUN apt-get update


#-- Instalation of dependencies
RUN apt-get install -y python g++ make nodejs mongodb-org openjdk-6-jre elasticsearch ruby1.9.1 ruby1.9.1-dev  git graphicsmagick unzip sendmail

#-- Official  PopIt Repo
RUN mkdir $src
RUN cd $src && git clone https://github.com/mysociety/popit 
ENV popit $src/popit

#-- Local correction, Doesn't work without it
ADD print.scss $popit/public/sass/

#-- Build PopIt
RUN cd $popit && make node-modules
RUN cp $popit/config/development.js-example $popit/config/development.js
RUN gem install sass --version=3.2.14 --no-rdoc --no-ri
RUN gem install compass --version=0.12.2 --no-rdoc --no-ri
#RUN mkdir /data && mkdir /data/db
RUN cd $popit && make css

#-- Config files for Parlamentoabierto.org.py
ADD init.sh $popit/
ADD default.js $popit/config/

VOLUME ["/src"]

#-- Run it!
CMD sh $popit/init.sh

