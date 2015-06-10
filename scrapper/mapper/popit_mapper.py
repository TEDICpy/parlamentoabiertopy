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
from popit_config import api_key, instance, hostname, port, user, password, api_key 
from popit_config import api_version
from popit_config import mongo_host, mongo_port


mg_client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
mdb = mg_client.silpy01
senadores = mdb.senadores


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
    else:
        print "ya existe membresia"

def create_committees(data):
    comision_id = None
    post_id = None
    print data
    if 'name' in data:
        print 'creating committee ' + name 
        name = data['name']
        #committee id generated for further references
        com_id = hashlib.sha1(name.encode('latin-1')).hexdigest()
        person_id = data['person_id']
        r = requests.get(url_string + '/organizations/' + com_id)
        com = r.json()
        if 'result' in com and 'id' in com['result'] and com['result']['id'] == com_id:
            result = com['result']
            comision_id = result['id']
        else:    
            committee = {'name': name, 'id': com_id, 'classification': 'Comision'}
            if 'link' in data: 
                committee['links'] = [{'url': data['link'], 'note': 'enlace'}]
            result = api.organizations.post(committee)
            comision_id = result['result']['id']
        if 'post' in data:
            #
            p_id = comision_id + hashlib.sha1(data['post'].encode('latin-1')).hexdigest()
            r = requests.get(url_string + '/posts/' + p_id)
            if r.status_code == 404:
                post = {'id': p_id,
                        'label': data['post'],
                        'organization_id': comision_id,
                        'role': data['post']
                        }
                res = api.posts.post(post)
                if 'result' in res and 'id' in res['result']:
                    post_id = res['result']['id']
            else: 
                post_id = p_id
        if comision_id and person_id:
            data = {
                'organization_id': comision_id,
                'person_id': person_id
                }
            if post_id:
                data['post_id'] = post_id 
            mem = create_membership(data)
   
def create_party(data):
    party_id = None
    p_id = hashlib.sha1(data['name'].encode('latin-1')).hexdigest()
    r = requests.get(url_string + '/organizations/' + p_id)
    if r.status_code == 404:
        data['classificatio'] = 'party'
        result = api.organizations.post(data)
        if 'result' in result and 'id' in result['result']:
            party_id = result['result']['id']
    else:
        party_id = p_id

def senador_post(data):
    new_sen = {}
    contact_details = []
    memberships = []
    if 'name'in data:
        #generated hash for unique identification
        sen_id = hashlib.sha1(data['name'].encode('latin-1')).hexdigest()
        r = requests.get(url_string + '/persons/' +sen_id)
        if r.status_code == 404:
            print 'Procesando datos, Senador: ' + data['name']
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
        else: 
            print 'Ya existe Senador: ' + data['name'] 
            

def delete_all_members():
    #gets all members and proceed to eliminate it from popit
    persons = api.persons.get()
    for person in persons:
        pass
    

senadores = mdb.senadores.find()
for sen in senadores:
    senador = senador_post(sen)

print api.organizations.get()

if __name__ == '__main__':
    pass


