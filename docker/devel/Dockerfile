FROM ubuntu:14.04
MAINTAINER Ivan Florentin <ivan@sinergetica.com>
RUN touch /etc/legislative-devel

ENV src /src
ENV billit /src/bill-it
ENV popit /src/pop-it
ENV write-it /src/write-it
ENV legislative /src/legislative

RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y  mc emacs vim vim-python-jedi python-jedi emacs24-common emacs-goodies-el
