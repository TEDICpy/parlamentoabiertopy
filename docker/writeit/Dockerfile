FROM ubuntu:14.04
MAINTAINER  Ivan Florentin <ivan@sinergetica.com>

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties  wget git sqlite3
RUN apt-get install -y python-pip python-dev libpython-dev libffi-dev libssl-dev g++  yui-compressor python-urllib3 
RUN wget -t0 -c https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.5.1.deb
RUN dpkg -i elasticsearch-1.5.1.deb 
RUN update-rc.d elasticsearch defaults 95 10
RUN /etc/init.d/elasticsearch start
RUN git clone https://github.com/ciudadanointeligente/write-it.git
RUN sqlite3 /data/writeit.db 
ADD settings.py /wrtite-it/writeit/
RUN cd /write-it/  && pip install -r requirements.txt 
#RUN cd /write-it && ./manage.py syncdb 
#RUN cd /write-it && ./manage.py migrate
#RUN cd config_examples/
#RUN ./manage.py 
#RUN mkvirtualenv writeit
#RUN . ../venv/bin/activate
#RUN vim writeit.settings
#RUN cp settings.py settings.py.original
#RUN git clone https://github.com/ciudadanointeligente/write-it.git
#RUN . venv/bin/activate
#RUN ./manage.py syncdb && ./manage.py migrate
#RUN ./manage.py runserver
#RUN ./manage.py loaddata example_data.yaml
#RUN ./manage.py runserver
#RUN ./manage.py runserver
CMD cd /write-it && python manage.py runserver 0.0.0.0:8000
#RUN python manage.py runserver 0.0.0.0:8000
#RUN python manage.py runserver 192.168.122.77:9090
#RUN python manage.py runserver 192.168.122.77:8000
#RUN python manage.py runserver 192.168.122.77:8000
#RUN mv writeit.db writeit.db.old
#RUN ./manage.py syncdb && ./manage.py migrate
#RUN python manage.py runserver 192.168.122.77:8000
#RUN sqlite3 writeit.db 
#RUN python manage.py runserver 192.168.122.77:8000
#ADD init.sh /write-it
