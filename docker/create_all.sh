##
## Crear todas las imagenes
##

echo "Creating Data Container..."
cd data
./create_data.sh

echo "Creating Popit..."
cd ../popit/
./build_image.sh
#./create_container.sh



echo "Creating BillIt..."
cd ../billit/
./build_image.sh
#./create_container.sh


#comento ya que no estamos 
#usando esta instancia
#echo "Creating WriteIt..."
#cd ../writeit/
#./build_image.sh
#./create_container.sh


echo "Creating Legislative..."
cd ../legislative
./build_image.sh
#./create_container.sh



