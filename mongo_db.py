from pymongo import MongoClient

client = MongoClient('localhost', 27017)

class SilpyMongoClient(object):
    

    def __init__(self):
        #connect to the database
        self.db = client.silpy_test
        
    def save_projects(self, projects):
        db_projects = self.db.projects #initialize collection
        results = db_projects.insert_many(projects)# insert projects
        return results


    def save_senadores(self, senadores):
        db_senadores = self.db.senadores #initialize collection
        results = db_senadores.insert_many(senadores)# insert projects
        return results

    def save_comisiones_por_periodo(self, periodo, comisiones):
        db_comisiones_periodo = self.db.comisiones_periodo
        
        comisiones_periodo = {'periodo': periodo, 
                              'comisiones': comisiones}

        result_ids = db_comisiones_periodo.insert_one(comisiones_periodo) 
        return result_ids
