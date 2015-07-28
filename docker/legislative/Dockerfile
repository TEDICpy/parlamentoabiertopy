FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
#EXPOSE 22 3000

ENV LANG es_PY.UTF-8
ENV LANGUAGE es_PY.UTF-8:es
ENV src /src
ENV legislative /src/legislative

RUN touch /etc/legislative
RUN mkdir $src

#RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python-software-properties wget apt-file mc git vim \
  imagemagick sqlite3 libmysqlclient-dev libmagick++-dev ruby2.0 ruby2.0-dev \
  rails libsqlite3-dev

RUN touch /root/06

RUN cd $src && git clone https://github.com/ivanflorentin/legislative.git
#https://github.com/ciudadanointeligente/legislative.git


#RUN cd legislative
#RUN gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
#RUN \curl -sSL https://get.rvm.io | bash -s stable --rails
#RUN \curl -sSL https://get.rvm.io | bash -s stable --ruby --rails
# RUN .  ~/.rvm/scripts/rvm
# RUN echo "source ~/.rvm/scripts/rvm" >>~/.bashrc
# RUN rvm install ruby-2.0.0-p643
# RUN gem install bundler

RUN rm /usr/bin/ruby
RUN ln -s /usr/bin/ruby2.0 /usr/bin/ruby
RUN gem install mysql2 -v '0.3.18'
RUN cd $legislative && bundle install
ADD database.yml $legislative/config/
ADD legislative.yml $legislative/config/
RUN cd $legislative && sh setup.sh
ADD init.sh $legislative/

VOLUME ["/src"]

#CMD sh $legislative/init.sh
