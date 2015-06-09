##
## Crear todas las imagenes
##

echo "Creating Data Container..."
cd data
./create_data.sh

echo "Creating Popit..."
cd ../popit/
./build_image.sh
./create_container.sh
#docker start popit

echo "Creating Legislative..."
cd ../legislative
./build_image.sh
./create_container.sh
#docker start legislative


