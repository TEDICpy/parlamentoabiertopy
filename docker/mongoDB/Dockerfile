FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
ENV data /data
ENV src /src

# Sistem update and minimum needed packages
RUN touch /mongodb

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10

RUN echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.0.list

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties wget apt-file software-properties-common mongodb-org

CMD service mongod start
