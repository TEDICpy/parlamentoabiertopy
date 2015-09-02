docker build -t writeit .
echo "Ingresar los siguientes comando en consola: "
echo "    $ cd /src/write-it && ./manage.py syncdb "
echo "si va un error, volver a correr el comando "
echo "Luego correr el siguiente comando: "
echo " cd /src/write-it && ./manage.py migrate"
echo "Si no hay errores, salir del contenedor con control+d o $ exit  "
#docker run --name writeit_temp  -ti --volumes-from="data" --net="host" -v /src writeit_temp /bin/bash
#docker commit -a "Ivan Florentin" -m "writeit dbconfig" -p writeit_temp  writeit
#docker create --name writeit  --volumes-from="data" --net="host" -v /src writeit  python $writeit/manage.py runserver 0.0.0.0:8000

