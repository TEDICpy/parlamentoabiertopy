#
#create superuser
cd $writeit
pip install -r requirements.txt
#ython manage.py createsuperuse
service elasticsearch start
python manage.py runserver 0.0.0.0:8001


