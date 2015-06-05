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
        results = db_senadores.insert_many(senadores)# insert senadores, upsert maybe?
        return results

    
    def update_senadores(self, senadores):
        db_senadores = self.db.senadores
        results = []
        for senador in senadores:
            result = db_senadores.update({'id':senador['id']}, {'$set':senador}, True)
            results.append(result)
        return results

    def update_senador(self, senador):
        #self.db.senadores.find_one({'id': senador['id'])})
        db_senadores = self.db.senadores
        result = db_senadores.update({'id':senador['id']}, {'$set':senador}, True)
        return result

    def save_comisiones_por_periodo(self, periodo, comisiones):
        db_comisiones_periodo = self.db.comisiones_periodo
        comisiones_periodo = {'periodo': periodo, 
                              'comisiones': comisiones}
        result_ids = db_comisiones_periodo.insert_one(comisiones_periodo) 
        return result_ids

    def get_senator(self, id):
        return self.db.senadores.find_one({'id': str(id)})
        

    def save_diputados(self, diputados):
        db_diputados = self.db.diputados 
        results = db_diputados.insert_many(diputados)
        return results

    def update_diputados(self, diputados):
        db_diputados = self.db.diputados
        results = []
        for diputado in diputados:
            result = db_diputados.update({'id':diputado['id']}, {'$set':diputado}, True)
            results.append(result)
        return results

    def save_articles(self, articles):
        db_articles = self.db.articles
        result = db_articles.insert_many(articles)
        return result

