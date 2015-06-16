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
from popit_config import api_version, images_dir
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
    data['name'] = data['text']
    if 'name' in data:
        print 'creating committee ' + data['name'] 
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
   
def create_party(member_id, party_name):
    party_id = None
    data = {}
    #sometimes there are dots, sometimes there are not
    party_name = party_name.replace('.', '').strip()
    #generate unique id based on the party's short name
    p_id = hashlib.sha1(party_name.encode('latin-1')).hexdigest()
    print p_id, party_name
    r = requests.get(url_string + '/organizations/' + p_id)    
    if r.status_code == 404:
        print 'Creating party %s' %(party_name)
        data['id'] = p_id
        data['classification'] = 'Party'
        data['name'] = party_name
        result = api.organizations.post(data)
        if 'result' in result and 'id' in result['result']:
            party_id = result['result']['id']
            print party_id
    else:
        party_id = p_id
    data['organization_id'] = party_id
    data['person_id'] = member_id
    create_membership(data)

def create_chambers(member_id, origin):
    #creates a chamber if does not exists and liks to a member
    #origin: senadores, diputados
    data = {}
    origin_name = None
    chamber_id = None
    if origin == 'S':
        origin_name = 'Senado'
    elif origin == 'D':
        origin_name = 'Diputados'
    c_id = hashlib.sha1(origin_name.encode('latin-1')).hexdigest()
    r = requests.get(url_string + '/organizations/' + c_id)
    if r.status_code == 404:
        print 'Creating  %s' %(origin_name)
        chamber = {}
        chamber['id'] = c_id
        chamber['name'] = origin_name
        chamber['classification'] = 'Chamber'
        result = api.organizations.post(chamber)
        if 'result' in result and 'id' in result['result']:
            chamber_id = result['result']['id']
    else:
        chamber_id = c_id
    data['organization_id'] = chamber_id
    data['person_id'] = member_id
    create_membership(data)
    
def member_post(data, origin):
    #create party if it does not exists 
    new_member = {}
    contact_details = []
    memberships = []
    if 'name'in data and 'id' in data:
        #generated hash for unique identification
        #hashlib.sha1(data['name'].encode('latin-1')).hexdigest()
        member_id = data['id']#better use the id from silpy
        r = requests.get(url_string + '/persons/' +member_id)
        if r.status_code == 404:
            print 'Procesando datos: ' + data['name']
            new_member['id'] = member_id        
            new_member['name'] = data['name']
            new_member['img'] = data['img']
            if 'cv' in data:
                new_member['summary'] = data['cv']
                new_member['biography'] = data['cv']
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
            new_member['contact_details'] = contact_details 
            result =  api.persons.post(new_member)
            if 'result' in result and 'id' in result['result']:
                person_id = result['result']['id']
                #if the member is part of the senate or the chamber of deputies
                create_chambers(person_id, origin)
                #the party the member belongs
                create_party(person_id, data['party'])
                upload_member_image(person_id, data)
                #commitee creation and association
                if 'committees' in data:
                    for c in  data['committees']:
                        c['person_id'] = person_id
                        com = create_committees(c)
        else:
            print 'Ya existe el Miembro: ' + data['name'] 
            
        
def upload_member_image(member_id, data):
    #member_id: the person id in popit
    #data: a dict that must contain
    #    id: the id in silpy, which is also the filename of the image
    #    img: the source of the img
    filename= data['id'] + '.jpg'
    fp = open(images_dir + filename)
    result = api.persons(id=member_id)\
                .image.post({'source': data['img'],
                            'notes':'Official Portrait'},
                            files={'image': fp})

def map_popit():
    diputados = mdb.diputados.find()
    for d in diputados:
        diputado = member_post(d, 'D')

    senadores = mdb.senadores.find()
    for sen in senadores:
        senador = member_post(sen, 'S')


if __name__ == '__main__':
    pass

