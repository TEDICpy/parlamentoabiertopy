from pymongo import MongoClient

client = MongoClient('localhost', 27017)

class SilpyMongoClient(object):

    def __init__(self):
        #connect to the database
        self.db = client.silpy01
        
    def save_projects(self, projects):
        db_projects = self.db.projects #initialize collection
        results = db_projects.insert_many(projects)# insert projects
        return results

    def upsert_projects(self, projects):
        #saves a list of projects and returns the list of
        #object ids
        results = []
        db_projects = self.db.projects #initialize collection        
        for project in projects:
            id = project['id']
            print 'upserting project %s' %(id)
            result = db_projects.update({'id':id}, {'$set':project}, True)
            results.append(id)
            print result
        return results
    
    def save_senadores(self, senadores):
        db_senadores = self.db.senadores #initialize collection
        results = db_senadores.insert_many(senadores)# insert senadores, upsert maybe?
        return results
    
    def update_senadores(self, senadores):
        db_senadores = self.db.senadores
        results = []
        project_ids = []
        for senador in senadores:
            if 'projects' in senador:
                project_ids = self.upsert_projects(senador['projects'])
            result = db_senadores.update({'id':senador['id']}, {'$set':senador}, True)
            results.append(result)
        return results

    def update_senador(self, senador):
        #self.db.senadores.find_one({'id': senador['id'])})
        db_senadores = self.db.senadores
        if 'projects' in senador:
            project_ids = self.upsert_projects(senador['projects'])
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

    def update_diputado(self, diputado):
        db_diputados = self.db.diputados
        if 'projects' in diputado:
            project_ids = self.upsert_projects(diputado['projects'])
        result = db_diputados.update({'id':diputado['id']}, {'$set':diputado}, True)
        return result

    def update_diputados(self, diputados):
        db_diputados = self.db.diputados
        results = []
        for diputado in diputados:
            if 'projects' in diputado:
                project_ids = self.upsert_projects(diputado['projects'])
            result = db_diputados.update({'id':diputado['id']}, {'$set':diputado}, True)
            results.append(result)
        return results

    def update_diputados_by_name(self, diputados):
        db_diputados = self.db.diputados
        results = []
        for diputado in diputados:
            result = db_diputados.update({'name':diputado['name']}, {'$set':diputado}, True)
            results.append(result)
        return results

    def update_diputado_by_name(self, diputado):
        db_diputados = self.db.diputados
        d = db_diputados.find_one({'name':diputado['name']})
        del d['_id']
        diputado.update(d)
        result = db_diputados.update({'name':diputado['name']},{'$set':diputado}, True)
        return result

    def get_article_by_url(self, url):
        db_articles = self.db.articles
        article = db_articles.find_one({"url":url})
        return article
    
    def save_article(self, article):
        db_articles = self.db.articles
        result = db_articles.insert(article)
        return result
    
    def save_articles(self, articles):
        db_articles = self.db.articles
        result = db_articles.insert_many(articles)
        return result

    def get_all_senators(self):
        db_senadores = self.db.senadores
        return db_senadores.find()

    def get_all_deputies(self):
        db_diputados = self.db.diputados
        return db_diputados.find()

