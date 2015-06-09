FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>


# Sistem update and minimum needed packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties 
RUN apt-get install -y wget 
RUN apt-get install -y apt-file
#RUN apt-file search add-apt-repositoryapt-file 
RUN apt-get -y install software-properties-common

#---- PopIt specific package dependencies Repositories
RUN echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
RUN wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
RUN echo 'deb http://packages.elasticsearch.org/elasticsearch/0.90/debian stable main' | sudo tee /etc/apt/sources.list.d/elasticsearch.list
RUN add-apt-repository ppa:chris-lea/node.js
RUN apt-get update


#-- Instalation of dependencies
RUN apt-get install -y python g++ make nodejs
RUN apt-get install -y mongodb-org
RUN apt-get install -y openjdk-6-jre 
RUN apt-get install -y elasticsearch
RUN apt-get install -y ruby1.9.1 
RUN apt-get install -y ruby1.9.1-dev 
RUN apt-get install -y git 
RUN apt-get install -y graphicsmagick 
RUN apt-get install -y unzip 
RUN apt-get install -y sendmail

#-- Official  PopIt Repo
RUN git clone https://github.com/mysociety/popit 

#-- Local correction, Doesn't work without it
ADD print.scss /popit/public/sass/
#-- Build PopIt
RUN cd popit
RUN cd /popit && make node-modules
RUN cp /popit/config/development.js-example /popit/config/development.js
RUN gem install sass --version=3.2.14 --no-rdoc --no-ri
RUN gem install compass --version=0.12.2 --no-rdoc --no-ri
#RUN mkdir /data && mkdir /data/db
RUN cd /popit && make css

#-- Config files for Parlamentoabierto.org.py
ADD init.sh /popit/
ADD default.js /popit/config/


#-- Run it!
CMD sh /popit/init.sh

