#echo $POPIT_PORT_3000_TCP_ADDR " popit.parlamentoabierto.org.py popit" >> /etc/hosts
#echo $POPIT_PORT_3000_TCP_ADDR " parlamento.popit.parlamentoabierto.org.py parlamento" >> /etc/hosts

cd $legislative && rails s --port 8003
