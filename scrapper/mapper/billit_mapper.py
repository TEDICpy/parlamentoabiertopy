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

projects = mdb.projects.find()#{"_id" : "55c214cbada5cdb309e4ac8c"})

i = 0


for p in projects:
    print "loading bill with uuid= %s" %(p['id'])
    bill = Bill()
    if 'file' in  p:
        bill.uid = p['file'] #use nro de expediente?
    if 'title' in p:
        bill.title = p['title']
    if 'entry_date' in p:
        bill.creation_date = p['entry_date']
    if 'info' in p:
        if 'subject' in p['info']:
            bill.title = p['info']['subject']
        if 'heading' in p['info']:
            bill.abstract = p['info']['heading']
        if 'stage' in p['info']:
            bill.stage = p['stage']['stage']
        if 'sub_stage' in p['info']:
            bill.substage = p['stage']['sub_stage']
        if 'status' in p['info']:
            bill.status = p['stage']['status']
        if 'importance' in p['info']:
            bill.current_priority = p['info']['importance']
        if 'origin' in p['info']:
            bill.source = p['info']['origin']

    #documents
    bill.documents = []
    if 'documents' in p:
        for doc in p['documents']:
            document = Document()
            if 'registration_date' in doc:
                document.date = doc['registration_date']#, :type => DateTime
            if 'type' in doc:
                document.type = doc['type']#, :type => String
            # document.number#, :type => String
            # document.step = doc['']#, :type => String
            # document.stage = doc['']#, :type => String
            # document.chamber = doc['']#, :type => String
            # document.link = doc['']#, :type => String
            bill.documents.append(document.__dict__)
 
    #Directives
    bill.directives = []
    if 'directives' in p:
        if p['directives']:
            for d in p['directives']:
                directive = Directive()
                directive.date = d['date']#, :type => DateTime
                directive.step = d['result'] #, :type => String
                #directive.stage #, :type => String ?
                #directive.link #, :type => String ?
                bill.directives.append(directive.__dict__)

    #TODO: how do we relate it with popit?
    bill.authors = []
    if 'authors' in p:
        for author in p['authors']:
            bill.authors.append(author['name'])

    #paperworks
    bill.paperworks = []
    if 'paperworks' in p:
        for paperwork in p['paperworks']:
            new_paperwork = Paperwork()
            print paperwork
            if 'session' in paperwork:
                new_paperwork.session = paperwork['session']
            if 'date' in paperwork:
                new_paperwork.date = paperwork['date']
            if 'chamber' in paperwork:
                new_paperwork.chamber = paperwork['chamber']
            if 'stage' in paperwork:
                new_paperwork.stage = paperwork['stage']
            #new_paperwork.description = paperwork['']
            bill.paperworks.append(new_paperwork.__dict__)
    #if 'estage' in p:
    #bill[''] = p['']
    i = i + 1
    print json.dumps(bill.__dict__)
    r = requests.post(host + '/bills', data=json.dumps(bill.__dict__))
    print "------------------------------------------------------------------------------  " , i
    print r.content
#    if i > 50:
#        break
