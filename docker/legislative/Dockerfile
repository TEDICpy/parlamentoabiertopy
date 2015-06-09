FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
#EXPOSE 22 3000

#RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python-software-properties 
RUN apt-get install -y wget 
RUN apt-get install -y apt-file
RUN apt-get install -y mc git vim imagemagick sqlite3 libmysqlclient-dev
RUN apt-get install -y libmagick++-dev
RUN apt-get install -y ruby2.0 ruby2.0-dev
RUN apt-get install -y rails
RUN apt-get install -y libsqlite3-dev
RUN git clone https://github.com/ciudadanointeligente/legislative.git
RUN cd legislative
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
RUN cd /legislative && bundle install
RUN cd /legislative && sh setup.sh 
ADD database.yml /legislative/config/
ADD legislative.yml /legislative/config/
ADD init.sh /legislative/
CMD sh /legislative/init.sh
