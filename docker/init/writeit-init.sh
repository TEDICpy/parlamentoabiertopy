#
#create superuser
cd $writeit
pip install -r requirements.txt
#ython manage.py createsuperuse
service elasticsearch start
/etc/init.d/rabbitmq-server start
export C_FORCE_ROOT=true
python manage.py celery worker &
python manage.py runserver 0.0.0.0:8001


