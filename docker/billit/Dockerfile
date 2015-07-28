FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
RUN touch /etc/bill-it

ENV src /src
ENV billit /src/bill-it

RUN apt-get update
RUN apt-get -y upgrade

#install ruby 2.1
RUN sudo apt-get install -y software-properties-common
RUN sudo apt-add-repository ppa:brightbox/ruby-ng
RUN sudo apt-get update

#RUN apt-get install -y  ruby1.9.1 ruby1.9.1-dev make git ruby2.0 ruby2.0-dev  mongodb g++
RUN apt-get install -y  ruby1.9.1 ruby1.9.1-dev make git ruby2.1 ruby2.1-dev  mongodb g++

RUN sudo apt-get  install -y  ruby-switch
RUN ruby-switch --set ruby2.1
 
RUN gem install nio4r -v '1.0.0'
RUN gem install bcrypt -v '3.1.7'
RUN gem install bundler

RUN apt-get install -y openjdk-7-jdk

RUN mkdir $src
RUN cd $src && git clone https://github.com/ciudadanointeligente/bill-it.git
RUN cd $billit  && bundle install

RUN cp $billit/config.ru.example $billit/config.ru
RUN cp $billit/config/sunspot.yml.example $billit/config/sunspot.yml
RUN cp $billit/config/mongoid.yml.example $billit/config/mongoid.yml
RUN cp $billit/config/hateoas.yml.example $billit/config/hateoas.yml

VOLUME ["/src"]
RUN touch $billit/init.sh
#RUN  \curl -sSL https://get.rvm.io | bash -s stable --ruby=jruby --gems=rails
ADD init.sh $billit/
CMD sh $billit/init.sh
