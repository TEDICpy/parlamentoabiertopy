FROM ubuntu:16.04
MAINTAINER Lupa <lupa@tedic.org>

ENV DEBIAN_FRONTEND noninteractive
ENV LANG es_PY.UTF-8
ENV LANGUAGE es_PY.UTF-8:es
ENV SRC /src
ENV LEG /src/legislative
ENV REPO https://github.com/TEDICpy/legislative.git

RUN mkdir -p $LEG

RUN apt-get update && \
	&& apt-get upgrade -y \
	&& apt-get install -y python-software-properties wget apt-file mc git vim \
                   imagemagick sqlite3 libmysqlclient-dev libmagick++-dev ruby2.0 ruby2.0-dev \
                   rails libsqlite3-dev
WORKDIR $SRC
RUN git clone $REPO

RUN rm /usr/bin/ruby \
	&& ln -s /usr/bin/ruby2.0 /usr/bin/ruby \
	&& gem install mysql2 -v '0.3.18'

WORKDIR $LEG
RUN bundle install

ADD init.sh $LEG/
ADD database.yml $LEG/config/
ADD legislative.yml $LEG/config/
ADD hosts /etc/
RUN /bin/bash setup.sh

CMD /bin/bash $LEG/init.sh
