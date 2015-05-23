"""
Mapper para instancia PopIt 
Proyecto parlamentoabierto.org.py


"""

__author__ = "Ivan Florentin<ivan@sinergetica.com>"
__version__ = "0.0.1"

from popit_api import PopIt
import slumber
from requests.auth import AuthBase
import pymongo
import requests
import json
import hashlib

mg_client = pymongo.MongoClient(host='localhost', port=27017)
mdb = mg_client.silpy_test
senadores = mdb.senadores


instance = 'test'
hostname = 'test.popit.tdic'
port = 3000
api_version = 'v0.1' 
user = "i@a.com"
password = "asdqwe123"
api_key = 'e221fbd3018b4be18556263f5ff1f58d0a592545' 


class PopItApiKeyAuth(AuthBase):
    def __init__(self, api_key):
        self.api_key = api_key
    def __call__(self, r):
        r.headers['Apikey'] = str(self.api_key)
        return r

auth_key = PopItApiKeyAuth(api_key=api_key)
api = slumber.API("http://test.popit.tdic:3000/api/v0.1", auth=auth_key)

def create_membership(data):
    if 'organization_id' in data: 
        organization_id = data['organization_id']
    else: 
        if 'organization' in data:
            organization_id = create_organization(data['organization'])
        else_:
            raise "cannot create membership or organization, no data supplied"
    person_id = data['person_id']
    membership_id = organization_id + person_id
    mem = api.membership.get(membership_id)
    print mem


def committees_post(data):
    #api.note.get(title__startswith="Bacon")
    comision_id = None
    nombre = data['nombre']
    #nom_id = hashlib.sha1(nombre.encode('ascii', errors='ignore')).hexdigest()
    #print "sha1 " , nom_id
    person_id = data['person_id']
    r = requests.get('http://test.popit.tdic:3000/api/v0.1/organizations/' + nombre)
    com = r.json()
    #print('COM: ', com)
    if 'result' in com and 'name' in com['result'] and com['result']['name'] == nombre:
        result = com['result']
        #print "encontrado ", result['id']
        comision_id = result['id']
    else:    
        committee = {'name': nombre, 'id': nombre}
        result = api.organizations.post(committee)
        #print "creando: " , result['result']['id']
        comision_id = result['result']['id']
        #print "Nuevo: ", comision_id
    if comision_id and person_id:
        data = {
            'organization_id': comision_id,
            'person_id': person_id,
            'role': 'Miembro',
            'label': 'label',
            }
        mem = create_membership(data)
        membership_id =  comision_id+person_id
        q_str = 'http://test.popit.tdic:3000/api/v0.1/memberships/'+membership_id
        print "q:string: ", q_str
        r = requests.get(q_str)
        print "codigo", r.content
        res = r.json()
        print "membership_id " , membership_id
        print "resultado membresia get", res
        if 'result' in res and 'id' in res['result']:
            print "resultado de membresia: ", res['result']
        else:     
            mem = {
                    'id': membership_id,
                    'label': 'Miembro',
                    'role': 'Miembro',
                    'person_id': person_id,
                    'organization_id': comision_id,
                    }
            result = api.memberships.post(mem)
            #print "membership ", result['result']['id'] 

    

def senador_post(data):
    new_sen = {}
    contact_details = []
    memberships = []
    if 'name'in data:
        new_sen['name'] = data['name']
    if 'email' in data:
        contact_details.append({
            'type':'email',
            'label': 'Correo Electronico',
            'value': data['email'],
            'note': ''
            })
    if 'phone' in data:
         contact_details.append({
            'type':'phone',
            'label': 'Telefono',
            'value': data['phone'],
            'note': ''
            })
    new_sen['contact_details'] = contact_details 
    result =  api.persons.post(new_sen)
    if 'result' in result and 'id' in result['result']:
        person_id = result['result']['id']
        #print "senador", person_id 
        if 'committees' in data:
            for c in  data['committees']:
                c['person_id'] = person_id
                com = committees_post(c)
            #print(com)    
    
   #return api.persons.post(new_sen)

senadores = mdb.senadores.find()
for sen in senadores:
    senador = senador_post(sen)
    #print(senador['result']['id'])




if __name__ == '__main__':
    pass


