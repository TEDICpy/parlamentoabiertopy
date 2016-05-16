FROM ubuntu:14.04
MAINTAINER Demian Florentin <demian@tedic.org>
ENV data /data
ENV src /src
ENV votaciones $src/PAVotaciones

# Sistem update and minimum needed packages
RUN touch /popit.01
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get -y install lamp-server^

