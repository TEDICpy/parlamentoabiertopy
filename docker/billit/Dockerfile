FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>

RUN apt-get install -y  ruby1.9.1 ruby1.9.1-dev make

RUN apt-get install -y git ruby2.0 ruby2.0-dev  mongodb 

RUN gem install nio4r -v '1.0.0'

RUN gem install bundler



RUN git clone https://github.com/ciudadanointeligente/bill-it.git

RUN cd /bill-it && bundle install

#RUN  \curl -sSL https://get.rvm.io | bash -s stable --ruby=jruby --gems=rails
#ADD init.sh /billit/
#CMD sh /billit/init.sh
