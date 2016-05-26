FROM ubuntu:14.04
MAINTAINER Lupa <admin@tedic.org>

ENV DEBIAN_FRONTEND noninteractive
ENV SRC /src
ENV BILLIT /src/bill-it
ENV DATA /data
ENV REPO https://github.com/ciudadanointeligente/bill-it.git

RUN apt-get update \
	&& apt-get -y upgrade

RUN apt-get install -y software-properties-common \
	&& add-apt-repository -y ppa:brightbox/ruby-ng \
	&& apt-get update \
	&& apt-get install -y ruby1.9.1 make git ruby2.1 ruby2.1-dev mongodb g++ ruby-switch openjdk-7-jdk
#RUN ruby-switch --set ruby2.1

RUN gem install magic_encoding bundler \
	&& gem install nio4r -v '1.0.0' \
	&& gem install bcrypt -v '3.1.7'

# Bajo el codigo
RUN mkdir -p $BILLIT
WORKDIR $SRC
RUN git clone $REPO

# Instalo
WORKDIR $BILLIT
RUN bundle install

# Copio los achivos de configuracion
RUN cp config.ru.example config.ru
RUN cp config/sunspot.yml.example config/sunspot.yml
RUN cp config/mongoid.yml.example config/mongoid.yml
RUN cp config/hateoas.yml.example config/hateoas.yml

RUN cd $BILLIT && magic_encoding

ADD init.sh $BILLIT/

CMD ["$BILLIT/init.sh"]
