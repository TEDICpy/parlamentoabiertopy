FROM ubuntu:16.04
MAINTAINER Lupa <admin@tedic.org>

ENV DEBIAN_FRONTEND noninteractive
ENV SRC /src
ENV BILLIT /src/bill-it
ENV DATA /data
ENV REPO

RUN apt-get update \
	&& apt-get -y upgrade

RUN sudo apt-get install -y software-properties-common \
	sudo apt-add-repository ppa:brightbox/ruby-ng \
	ruby1.9.1 ruby1.9.1-dev make git ruby2.1 ruby2.1-dev  mongodb g++ ruby-switch openjdk-7-jdk
RUN ruby-switch --set ruby2.1

RUN gem install magic_encoding bundler \
	&& gem install nio4r -v '1.0.0' \
	&& gem install bcrypt -v '3.1.7'

RUN mkdir -p $BILLIT
WORKDIR $SRC
RUN git clone $REPO
WORKDIR $BILLIT
RUN bundle install

RUN cp $BILLIT/config.ru.example $BILLIT/config.ru
RUN cp $BILLIT/config/sunspot.yml.example $BILLIT/config/sunspot.yml
RUN cp $BILLIT/config/mongoid.yml.example $BILLIT/config/mongoid.yml
RUN cp $BILLIT/config/hateoas.yml.example $BILLIT/config/hateoas.yml

RUN cd $BILLIT && magic_encoding

ADD init.sh $BILLIT/

CMD sh $BILLIT/init.sh
