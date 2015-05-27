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
url_string = 'http://' + hostname + ':' + str(port) + '/api/' + api_version 
api = slumber.API(url_string, auth=auth_key)

def create_membership(data):

    organization_id = data['organization_id'] 
    person_id = data['person_id']
    membership_id = organization_id + person_id
    r = requests.get(url_string + '/memberships/' + membership_id)
    if r.status_code == 404:
        data['id'] = membership_id
        data['organization_id'] = organization_id
        mem = api.memberships.post(data)
        print 'membresia nueva.. id: ' + membership_id + '  ::  ' + mem['result']['id'] 
    else:
        print "ya existe membresia"

def committees_post(data):
    comision_id = None
    if 'name' in data:
        name = data['name']
        com_id = hashlib.sha1(name.encode('latin-1')).hexdigest()
        person_id = data['person_id']
        r = requests.get(url_string + '/organizations/' + com_id)
        com = r.json()
        if 'result' in com and 'id' in com['result'] and com['result']['id'] == com_id:
            result = com['result']
            print "encontrado ", result['id']
            comision_id = result['id']
        else:    
            committee = {'name': name, 'id': com_id}
            result = api.organizations.post(committee)
            comision_id = result['result']['id']
            print "Nuevo: ", comision_id
        if comision_id and person_id:
            data = {
                'organization_id': comision_id,
                'person_id': person_id,
                'role': 'Miembro',
                'label': 'label',
                }
            mem = create_membership(data)
   

def senador_post(data):
    new_sen = {}
    contact_details = []
    memberships = []
    if 'name'in data:
        sen_id = hashlib.sha1(data['name'].encode('latin-1')).hexdigest()
        r = requests.get(url_string + '/persons/' +sen_id)
        if r.status_code == 404:
            new_sen['id'] = sen_id        
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
                if 'committees' in data:
                    for c in  data['committees']:
                        c['person_id'] = person_id
                        com = committees_post(c)
            

senadores = mdb.senadores.find()
for sen in senadores:
    senador = senador_post(sen)




if __name__ == '__main__':
    pass


