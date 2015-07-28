#-*- coding: utf-8 -*-
'''

@author: Demian Florentin<demian@sinergetica.com>
'''
import requests
import json
import uuid
from datetime import datetime
import pymongo
host = 'http://localhost:3500'
secret_token = '75cc973db60d3e07beaa1630c4cb37ded228e5bb71853be068a573b1a2ee385379111f9b12847b285a7e2c2b2f918b2902f4edb04046319cf41148a642fa53d3'

mg_client = pymongo.MongoClient(host='localhost', port=27017)
mdb = mg_client.silpy01
senadores = mdb.senadores

headers = {"Content-Type": "application/json",
           "X-CSRF-Token": secret_token}


class Bill(object):
    ''' 
    class bassed on the model from 
    bill-it/app/models/bill.rb

    ''' 
    uid= "" #type: String
    title= "" #, type: String
    abstract= "" #, type: String
    creation_date= "" #, type: Time
    source= "" #, type: String
    initial_chamber= "" #, type: String
    stage= "" #, type: String
    sub_stage= "" #, type: String
    status= "" #, type: String
    resulting_document= "" #, type: String
    merged_bills= "" #, type: Array
    subject_areas= "" #, type: Array
    authors= "" #, type: Array
    publish_date= "" #, type: Time
    tags= "" #, type: Array
    bill_draft_link= "" #, type: String
    current_priority= "" #, type: String

    
class Paperwork(object):
   
  session = ''#, :type => String
  date = ''#, :type => DateTime
  description = ''#, :type => String
  stage = ''#, :type => String
  chamber = ''#, :type => String
  bill_uid = ''#, :type => String
  timeline_status = ''#, :type => String


class Directive(object):
    pass    

class Document(object):
    pass


projects = mdb.projects.find()
for p in projects:
    print "loading bill with uuid= %s" %(p['id']) 
    bill = Bill()
    bill.uid = p['id']
    bill.title = p['title']
    bill.creation_date = p['entry_date']
    bill.title = p['info']['subject']
    bill.abstract = p['info']['heading']
    bill.stage = p['stage']['stage']
    bill.substage = p['stage']['sub_stage']
    bill.status = p['stage']['status']
    bill.current_priority = p['info']['importance']
    bill.source = p['info']['origin']

    #documents
    bill.documents = []
    for doc in p['documents']:
        document = Document()
        document.date = doc['registration_date']#, :type => DateTime
        document.type = doc['type']#, :type => String
        # document.number#, :type => String
        # document.step = doc['']#, :type => String
        # document.stage = doc['']#, :type => String
        # document.chamber = doc['']#, :type => String
        # document.link = doc['']#, :type => String
        bill.documents.append(document.__dict__)
        
    #Directives
    bill.directives = []
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
    for author in p['authors']:
        bill.authors.append(author['name'])

    #paperworks
    bill.paperworks = []
    for paperwork in p['paperworks']:
        new_paperwork = Paperwork()
        print paperwork
        new_paperwork.session = paperwork['session']
        new_paperwork.date = paperwork['date']
        new_paperwork.chamber = paperwork['chamber']
        new_paperwork.stage = paperwork['stage']
        #new_paperwork.description = paperwork['']
        bill.paperworks.append(new_paperwork.__dict__)
        
    #bill[''] = p['']
    print json.dumps(bill.__dict__)
    r = requests.post(host + '/bills', data=json.dumps(bill.__dict__))
    print "------------------------------------------------------------------------------"
    print r.content
    


