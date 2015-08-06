#-*- coding: utf-8 -*-

#In this file we process data comming from
#http://www.senado.gov.py
#TODO:

import traceback
import httplib
import json
import urllib
import unicodedata
from bs4 import BeautifulSoup

from utils import utils
                               
application_x_www_form_urlencoded='application/x-www-form-urlencoded'
headers = {}
headers['Content-Type'] = application_x_www_form_urlencoded
headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'

host= 'www.senado.gov.py'
base_url = 'http://www.senado.gov.py/'
port= 80

debuglevel = 0
#Averiguar de donde quitar
#E. Últimas noticias del legislador/a: Departamento Prensa de su Cámara / Noticias en medios de difusión
#F. Producción parlamentaria: Comisiones que integra / Iniciativas presentados (*) / Votaciones recientes (*) / Participación en sesiones (ord/ext) (desde 2013) (*)

class SenadoresParser(object):

    # def __init__(self):
    #     path = 'resources/senadores/'
    #     self.nomina_html = read_file_as_string(path + 'lista.html')
    #     self.actividad = read_file_as_string(path + 'actividad_legislativa.html')
    #     self.dictamenes = read_file_as_string(path + 'dictamenes.html')
        
    def parse_senator_list(self, html):
        soup = BeautifulSoup(html)        
        #find table and extract parla_id
        senators = []
        table = soup.find('table', {'class':"table table-striped"})
        tr_list = table.find_all('tr')#first row is header
        for tr in tr_list:
            img = tr.find('img') #if there's an img its data            
            if img:
                td_list = tr.find_all('td')
                text = td_list[0].a.text#img.a.text
                name = text[text.index('.')+1 :len(text)].strip()
                href = td_list[0].a['href']
                id = href[href.index('id_parla=') : len(href)].replace('id_parla=','')
                
                senator  = {'id': id, 
                            'name': name.strip(),
                            'link': href,
                            'party': td_list[1].text.strip(),
                            'phone': td_list[2].text.strip(),
                            'email': td_list[3].a['href'].replace('mailto:', '')}
                senators.append(senator)

        return senators
        
    def parse_senator_info(self, data):
        projects = []
        soup = BeautifulSoup(data)
        cv = soup.find(id = '2-1-curriculum-vitae')#save as chunk of data?
        return cv.getText()
        
    def parse_senator_committees(self, html):      
        soup = BeautifulSoup(html)
        div_committees = soup.find(id = '2-5-comisiones')
        tr_list = div_committees.find_all('tr')
        tr_list = tr_list[1 : len(tr_list)] #remove header
        committees = []
        for tr in tr_list:
            td_list = tr.find_all('td')
            link = td_list[0].a['href']
            id = link[link.rfind('/')+1:]
            committee = {'id': id,
                         'name': td_list[0].text.strip(),
                         'post' : td_list[1].text.strip(),
                         'link': link}
            committees.append(committee)
        return committees

    def parse_senator_presented_projects(self, html):
        #2-3-proyectos-presentados
        soup = BeautifulSoup(html)
        presented_projects_tab = soup.find(id='2-3-proyectos-presentados')
        tbody = presented_projects_tab.table.tbody
        tr_list = tbody.find_all('tr', recursive=False)
        tr_list = tr_list[1:len(tr_list)]#remove header
        
        actividades = []
        for tr in tr_list:
            td_list = tr.find_all('td', recursive=False)
            actividad = {}
            date_text = td_list[0].text
            actividad['date'] = date_text[: date_text.index('.'):-1].strip()[::-1]
            #actividad['fecha'] = td_list[0].text.strip()
            actividad['file'] = td_list[1].text.strip()
            acapite = td_list[2].text.strip()
            new_line = acapite.index('\n')
            actividad['heading'] = {'title':acapite[0:new_line].strip() , 
                                    'detail':acapite[new_line:].strip()}
            actividades.append(actividad)
        
        return actividades

    def parse_dictamenes(self, html):
        soup = BeautifulSoup(html)
        dictamenes = soup.find(id = u'2-6-dictámenes')#beware of the á
        tr_list = dictamenes.find_all('tr')
        tr_list = tr_list[1 : len(tr_list)] #remove header
        dictamenes = []
        for tr in tr_list:
            td_list = tr.find_all('td')
            text = td_list[0].text.strip()
            if text.find('.') != -1:
                expediente = text[text.index('.')+1 : text.index('\n')].strip()
                titulo = text[text.index('\n'):len(text)].strip()
                fecha = td_list[1].text.strip()
                sentido = td_list[2].text.strip()
                link = td_list[0].a['href']
                dictamen = {'file': expediente,
                            'title': titulo,
                            'date': fecha,
                            'direction': sentido,
                            'link': link}                
                dictamenes.append(dictamen)            
        return dictamenes

import sys
import httplib
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

from db.mongo_db import SilpyMongoClient

class SenadoresScrapper(object):

    def __init__(self):
        self.host = "http://www.senado.gov.py/"
        self.mongo = SilpyMongoClient()
        self.parser = SenadoresParser()
        self.browser = utils.get_new_browser()
        self.browser.get(self.host)
    
    def driver_quit(self):
        self.browser.quit()

    # def make_webdriver_wait(self, by, waited_element):
    #     try:
    #         wait = WebDriverWait(self.browser, 15)
    #         wait.until(EC.presence_of_element_located((by, waited_element)))
    #         print "Page is ready! Loaded: " + waited_element
        
    #     except TimeoutException:
    #         print "Loading took too much time!"

    # def _wait_document_ready(self, something):
    #     print something
    #     is_complete = self.browser.execute_script("return document.readyState;")
    #     if (is_complete == "complete"):
    #         return True

    def obtener_lista_de_senadores(self):
        url = base_url +  "index.php/senado/nomina/nomina-alfabetica"
        self.browser.get(url)        
        #wait here for something
        utils.wait_for_document_ready(self.browser)
        data = self.browser.page_source
        senadores = self.parser.parse_senator_list(data)
        #self.mongo.update_senadores(senadores)
        return senadores
            
    def extract_senators_data(self):
        try:
            senadores = self.obtener_lista_de_senadores()
            for s in senadores:
                id = s['id']
                s = self.get_member_info(s)
                #retrieve senator from db
                #senator = self.mongo.get_senator(id)
                #merge senator data from web and db
                #senator.update(s)
                #update senator to db
                self.mongo.update_senador(s)            
            self.browser.close()
        except Exception, err:
            print "WARNING: Improve Exception handling."
            traceback.print_exc()

    def get_member_info(self, senator):
        id = senator['id']
        print 'obteniendo info de senador ' + senator['name'] 
        url="http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=%s" %(id)
        self.browser.get(url)
        utils.make_webdriver_wait(By.CLASS_NAME, "IN-widget", self.browser)
        utils.make_webdriver_wait(By.ID, "2-1-curriculum-vitae", self.browser)
        data = self.browser.page_source
        #extracts comisiones
        committees = self.parser.parse_senator_committees(data)
        #extracts dictamenes
        dictamenes = self.parser.parse_dictamenes(data)
        cv = self.parser.parse_senator_info(data)
#        proyectos = self.parser.parse_senator_presented_projects(data)
        senator.update({'committees': committees,
                        'rulings': dictamenes,
                        'cv': cv})
        return senator

    def get_all_articles(self):
        #TODO: logic to retrieve older articles
        #and update when new articles appear
        #POST http://www.senado.gov.py/index.php/noticias
        #form param limit:"0" for all news 
        # limit 5 for last 5 news
        #the table with the class="table table-striped table-bordered"
        #contains the data
        # Other Parameters:  
        # filter-search:""
        # filter_order:""
        # filter_order_Dir:""
        # limitstart:""
        host = 'http://www.senado.gov.py'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'

        conn = httplib.HTTPConnection('www.senado.gov.py', 80)
        conn.debuglevel = 0
        conn.connect()
        #first retrieve list of news
        request = conn.request('POST', '/index.php/noticias',
                               'limit=0', headers)
        response = conn.getresponse()
        data = response.read()
        #extract data from the table where the  news are presented
        soup = BeautifulSoup(data)
        table = soup.find('table', {'class': 'table table-striped table-bordered'})
        tr_list = table.tbody.find_all('tr', recursive=False)

        #iterate over the list of news to extract each row
        for tr in tr_list:
            url = host + tr.a['href']
            article = self.mongo.get_article_by_url(url)
            if article == None:
                td_list = tr.find_all('td', recursive=False)
                article = {'date': td_list[1].text.strip()}
                article['url'] = url
                url = url.encode('utf-8')
                #call the url
                try:
                    #urls may contain non ascii characters
                    request = conn.request('POST', url, 'limit=5', headers)
                    response = conn.getresponse()
                    data = response.read()
                    news_soup = BeautifulSoup(data)
                    article_html = news_soup.find('article', {'class': 'article fulltext '})
                    article['content'] = article_html.getText().encode('utf-8')
                    self.mongo.save_article(article)
                except:
                    print "Failed extracting data from %s" %(article['url'])
            
        conn.close()        
        
    def obtener_dictamenes_de_senador(self, id):
        #id_parla
        #los dictamenes de cada senador se cargan al llamar al tab de dictamenes
        url = 'http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100056#2-6-dict%C3%A1menes'

