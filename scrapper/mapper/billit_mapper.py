#-*- coding: utf-8 -*-
'''

@author: Demian Florentin<demian@sinergetica.com>
'''
import requests
import json
import uuid
from datetime import datetime
import pymongo
from billit_model import Bill, Paperwork, Directive, Document

host = 'http://localhost:8002'
secret_token = '75cc973db60d3e07beaa1630c4cb37ded228e5bb71853be068a573b1a2ee385379111f9b12847b285a7e2c2b2f918b2902f4edb04046319cf41148a642fa53d3'

mg_client = pymongo.MongoClient(host='localhost', port=27017)
mdb = mg_client.silpy01
senadores = mdb.senadores

headers = {"Content-Type": "application/json",
           "X-CSRF-Token": secret_token}

def get_chamber(chamber):
    if chamber == "CAMARA DE DIPUTADOS":
        return "C. Diputados"
    if chamber == "CAMARA DE SENADORES":
        return "Senado"
    return chamber

def map_billit():
    offset = 50
    start = 0
    end = offset
    total = mdb.projects.count()
    while end < total:
        if (total - end) > offset:
            end += offset
        else:
            end = total
        projects = mdb.projects.find()[start:end]
        post_projects(projects)
        print "-------------------------"
        print "start " + str(start)
        print "end " + str(end)
        print "diff " + str(total - end)
        print "-------------------------"
        start = end
        
def post_projects(projects):
    for p in projects:
        print "loading bill with uuid= %s" %(p['id'])
        bill = Bill()
        if 'file' in  p:
            bill.uid = p['file'] 
            bill.scrap_id = p['id']
        if 'title' in p:
            bill.title = p['title']
        if 'entry_date' in p:
            bill.creation_date = p['entry_date']
        if 'info' in p:
            info = p['info']
            if 'origin' in info:
                bill.initial_chamber = get_chamber(info['origin'])
                bill.source = info['iniciativa']            
            #if 'subject' in p['info']:
            #    bill.title = p['info']['subject']
            if 'heading' in info:
                bill.abstract = info['heading']
            if 'importance'in info:
                if info['importance'] == "SIN URGENCIA":
                    bill.urgent = 'Simple'
                else:
                    bill.urgent = info['importance']
        if 'stage' in p:
            stage = p['stage']
            if 'stage' in stage:
                bill.stage = stage['stage']
            if 'sub_stage' in stage:
                bill.sub_stage = stage['sub_stage']
            if 'status' in stage:
                bill.status = stage['status']
        bill.authors = []
        if 'authors' in p:
            for author in p['authors']:
                bill.authors.append(author['id']+':'+author['name'])
        #paperworks
        bill.paperworks = []
        if 'paperworks' in p:
            for paperwork in p['paperworks']:
                new_paperwork = Paperwork()
                if 'session' in paperwork:
                    new_paperwork.session = paperwork['session']
                if 'date' in paperwork:
                    new_paperwork.date = paperwork['date']
                if 'chamber' in paperwork:
                    new_paperwork.chamber = get_chamber(paperwork['chamber'])
                if 'stage' in paperwork:
                    new_paperwork.stage = paperwork['stage']
                if 'result' in paperwork:
                    if 'value'in paperwork['result']:
                        new_paperwork.timeline_status = paperwork['result']['value']
                bill.paperworks.append(new_paperwork.__dict__)
        #documents
        bill.documents = []
        if 'documents' in p:
            for doc in p['documents']:
                document = Document()
                if 'registration_date' in doc:
                    document.date = doc['registration_date']#, :type => DateTime
                if 'type' in doc:
                    document.type = doc['type']#, :type => String
                    #TODO: generar link a documento
                    # document.number#, :type => String
                    # document.step = doc['']#, :type => String
                    # document.stage = doc['']#, :type => String
                    # document.chamber = doc['']#, :type => String
                    document.link = doc['name']#, :type => String
                    bill.documents.append(document.__dict__)
        #Directives
        bill.directives = []
        if 'directives' in p:
            if p['directives']:
                for d in p['directives']:
                    directive = Directive()
                    if 'date' in d:
                        directive.date = d['date']#, :type => DateTime
                    if 'result' in d:
                        directive.step = d['result'] #, :type => String
                    #directive.stage #, :type => String ?
                    #directive.link #, :type => String ?
                    bill.directives.append(directive.__dict__)
                    
        r = requests.post(host + '/bills', data=json.dumps(bill.__dict__))
        print "------------------------------------------------------------------------------  "
        print r.content
