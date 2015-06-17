FROM ubuntu:14.04
MAINTAINER Demian Florentin <demian@sinergetica.com>

#RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties 
RUN apt-get install -y wget 
RUN apt-get install -y apt-file
RUN apt-get install -y mongodb
RUN apt-get install -y git
RUN apt-get install -y emacs24-nox
RUN curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python
RUN easy_install pip
RUN pip install beautifulsoup4
RUN pip install PyMongo
RUN pip install selenium
RUN pip install requests
RUN pip install slumber 
RUN pip install PopIt-Python
RUN pip install click
RUN wget https://gist.githubusercontent.com/julionc/7476620/raw/b27b7e3b51b92be055ee46aefc0acfa459c0bb27/install_phantomjs.sh
RUN sh install_phantomjs.sh
RUN git clone https://github.com/demianfe/parlamentoabiertopy
