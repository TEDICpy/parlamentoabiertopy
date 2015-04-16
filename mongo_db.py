from pymongo import MongoClient

client = MongoClient('localhost', 27017)

class SilpyClient(object):
    

    def __init__(self):
        #connect to the database
        self.db = client.silpy_test
        
    def save_projects(self, projects):
        db_projects = self.db.projects #initialize collection
        results = db_projects.insert_many(projects)# insert projects
        return results






