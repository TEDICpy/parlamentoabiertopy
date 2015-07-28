FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
ENV data /data
ENV src /src

# Sistem update and minimum needed packages
RUN touch /etc/dns-server
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python-software-properties wget apt-file software-properties-common bind9 bind9utils

