FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
RUN touch /etc/bill-it

ENV src /src
ENV billit /src/bill-it

RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y  ruby1.9.1 ruby1.9.1-dev make git ruby2.0 ruby2.0-dev  mongodb g++

RUN gem install nio4r -v '1.0.0'

RUN gem install bundler


RUN mkdir $src
RUN cd $src && git clone https://github.com/ciudadanointeligente/bill-it.git
RUN cd $billit  && bundle install

RUN cp $billit/config.ru.example $billit/config.ru
RUN cp $billit/conig/hateoas.yml.example $billit/conig/hateoas.yml



VOLUME ["/src"]
RUN touch $billit/init.sh
#RUN  \curl -sSL https://get.rvm.io | bash -s stable --ruby=jruby --gems=rails
ADD init.sh $billit/
CMD sh $billit/init.sh
