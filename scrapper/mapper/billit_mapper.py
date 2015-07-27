'''

@author: Demian Florentin<demian@sinergetica.com>
'''
import requests
import json
import uuid
from datetime import datetime

host = 'http://localhost:3500'
secret_token = '75cc973db60d3e07beaa1630c4cb37ded228e5bb71853be068a573b1a2ee385379111f9b12847b285a7e2c2b2f918b2902f4edb04046319cf41148a642fa53d3'

mg_client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
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



b = Bill()
b.uid = str(uuid.uuid1())
b.title = "Bill title"
b.abstract = "abstract"
b.creation_date = datetime.now().strftime("%Y-%m-%d")
b.initial_chamber = "senadores"

source= "parlamento"
stage= "inicial"
sub_stage= "" 
status= "inicial" 
resulting_document= "doc" 
merged_bills= "" #, type: Array
subject_areas= "" #, type: Array
# authors= "" #, type: Array
# publish_date= "" #, type: Time
# tags= "" #, type: Array
# bill_draft_link= "" #, type: String
# current_priority= "" #, type: String

print "loading bill with uuid= %s" %(b.uid) 
senadores = mdb.senadores.find()
for sen in senadores:
    sen['uid'] = str(uuid.uuid1())
    
    r = requests.post(host + '/bills', data=payload)
    print r.content
    
#json.dumps(b.__dict__)    
