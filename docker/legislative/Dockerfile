FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>

ENV LANG es_PY.UTF-8
ENV LANGUAGE es_PY.UTF-8:es
ENV src /src
ENV legislative /src/legislative

RUN touch /legislative
RUN mkdir $src

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python-software-properties wget apt-file mc git vim \
  imagemagick sqlite3 libmysqlclient-dev libmagick++-dev ruby2.0 ruby2.0-dev \
  rails libsqlite3-dev

RUN touch /root/07

RUN cd $src && git clone https://github.com/ivanflorentin/legislative.git

RUN rm /usr/bin/ruby
RUN ln -s /usr/bin/ruby2.0 /usr/bin/ruby
RUN gem install mysql2 -v '0.3.18'
RUN cd $legislative && bundle install

#RUN touch /legislative.01

ADD init.sh $legislative/
ADD database.yml $legislative/config/
ADD legislative.yml $legislative/config/
ADD hosts /etc/
RUN cd $legislative && sh setup.sh

#CMD sh $legislative/init.sh
