#gets bills from database
#downloads files using static link
import pymongo
import os
import sys

mg_client = pymongo.MongoClient(host='localhost', port=27017)
mdb = mg_client.silpy01

total_downloaded = 0
base_dir = ''#base dir where all files should be located

def download_from_static_link(link, dir, filename):
    if not os.path.exists(base_dir+dir):
        os.makedirs(base_dir+dir)

    out = base_dir+dir+'/'+filename
    command = u'curl ' + link \
          +' -H "Host: sil2py.senado.gov.py"'\
          +' -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'\
          +' -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'\
          +' -H "Accept-Language: en-US,en;q=0.5"'\
          +' -H "Accept-Encoding: gzip, deflate"'\
          +' -H "Connection: keep-alive"'\
          +' -H "Content-Type: application/x-www-form-urlencoded"'\
          +' --compressed'\
          +' -o ' + out 
    command = command.encode('utf-8')
    os.system(command)
    return dir+filename

def download_files(bills):
    for bill in bills:
        print 'Downloading files for bill %s' %bill['id']
        dir = 'download/bills/%s/' %bill['info']['file']
        documents  = bill['documents']
        index = 0
        for doc in documents:
            dir = dir+'documents'
            print doc['link']
            doc['path'] = download_from_static_link(doc['link'], dir, doc['name'])
            bill['documents'][index] = doc
            index += 1
        print mdb.projects.update({'id':bill['id']}, {'$set':bill}, True)
            
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
    download_files(projects)
    start = end
    

# print '--------------------------------------------'
# print 'Total files downloaded %i' %total_downloaded
# print '--------------------------------------------'
