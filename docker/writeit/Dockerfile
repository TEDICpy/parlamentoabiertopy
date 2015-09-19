FROM ubuntu:14.04
MAINTAINER  Ivan Florentin <ivan@sinergetica.com>
EXPOSE 8000
LABEL "version"="1.0"
ENV data /data

ENV LANG es_PY.UTF-8
ENV LANGUAGE es_PY.UTF-8:es

RUN touch /writeit.0

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y wget git sqlite3
RUN apt-get install -y python-pip python-dev libpython-dev libffi-dev libssl-dev g++  yui-compressor python-urllib3
RUN wget -t0 -c https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.1.deb
RUN dpkg -i elasticsearch-1.5.1.deb
RUN update-rc.d elasticsearch defaults 95 10
RUN /etc/init.d/elasticsearch start

RUN mkdir /src
ENV src /src
ENV writeit /src/write-it
RUN cd $src && git clone https://github.com/ciudadanointeligente/write-it.git

RUN locale-gen es_PY.UTF-8

ADD settings.py $writeit/writeit/
#ADD init.sh $writeit
ADD db_init.sh /

RUN cd $writeit  && pip install -r requirements.txt
RUN echo "deb http://www.rabbitmq.com/debian/ testing main" >>/etc/apt/sources.list
RUN wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
RUN apt-key add rabbitmq-signing-key-public.asc

RUN apt-get install -y rabbitmq-server
#VOLUME ["/src"]
#RUN mkdir /data
#VOLUME ["/data"]

#RUN sqlite3 /data/writeit.db


#  levantar la imagen con
# $ docker run --name writeit -ti --volumes-from="data" --net="host" writeit /bin/bash
#
#    cd /write-it && ./manage.py syncdb   # <-- este comando correr 2 veces, la primera vez falla...
     		     		 	  # se encuentra documantado en las instrucciones
					  # de instalacion
#    cd /write-it && ./manage.py migrate
#
# Luego en otra consola mientras el contenedor aun esta corriendo:
#  $ docker commit -a "Ivan Florentin" -m "writeit dbconfig" -p writeit writeit:1
#
# para poner en produccion: 
# $sqlite3 /data/write-it.db
###  update django_site set domain = 'writeit.parlamentoabierto.org.py:8001';
# update django_site set domain = 'writeit.parlamentoabierto.org.py:8001' , name = 'writeit.parlamentoabierto.org.py' where id = 1;
#CMD cd /write-it && python manage.py runserver 0.0.0.0:8000


