docker run -d --name popit --volumes-from data --net=host -v /src popit sh /src/popit/init.sh

