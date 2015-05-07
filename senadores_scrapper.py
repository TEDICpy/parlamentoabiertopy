#-*- coding: utf-8 -*-

#In this file we process data comming from
#http://www.senado.gov.py
#TODO:

import httplib
import json
import urllib
import unicodedata
from bs4 import BeautifulSoup

from utils import *
                    
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
        
    def parese_senator_info(self):
        projects = []
        soup = BeautifulSoup(self.actividad)
        cv = soup.find(id = '2-1-curriculum-vitae')#save as chunk of data?
        
        # table2  = soup.find('table', {'class': 'table2'})
        # table_projects = soup.find(id = '2-3-proyectos-presentados')
        # tr_list = table_projects.find_all('tr')
        # tr_list = tr_list[1 : len(tr_list)] #remove header
        # for tr in tr_list:
        #    # project_td = pr.find_all('td')
        #     td_list = tr.find_all('td')
        #     project = {}
        #     date_text = td_list[0].text
        #     project['date'] = date_text[: date_text.index('.'):-1].strip()[::-1]
        #     project['folder'] = td_list[1].text.strip()
        #     project_column = td_list[2].text
        #     project['name'] = project_column[:project_column.index('\n')]
        #     project['details'] = project_column[ :project_column.index('\n'): -1][::-1].strip()
        #     projects.append(project)
 
        # return projects

    def parse_senator_committees(self, html):      
        soup = BeautifulSoup(html)
        div_committees = soup.find(id = '2-5-comisiones')
        tr_list = div_committees.find_all('tr')
        tr_list = tr_list[1 : len(tr_list)] #remove header
        committees = []
        for tr in tr_list:
            td_list = tr.find_all('td')
            committee = {'nombre': td_list[0].text.strip(),
                         'cargo' : td_list[1].text.strip(),
                         'link': td_list[0].a['href']}
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
            actividad['fecha'] = date_text[: date_text.index('.'):-1].strip()[::-1]
            #actividad['fecha'] = td_list[0].text.strip()
            actividad['expediente'] = td_list[1].text.strip()
            acapite = td_list[2].text.strip()
            new_line = acapite.index('\n')
            actividad['acapite'] = {'titulo':acapite[0:new_line].strip() , 'detalle':acapite[new_line:].strip()}
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
                dictamen = {'expediente': expediente,
                            'titulo': titulo,
                            'fecha': fecha,
                            'sentido': sentido,
                            'link': link}                
                dictamenes.append(dictamen)
            
        return dictamenes


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from mongo_db import SilpyMongoClient

class SenadoresScrapper(object):

    def __init__(self):
        self.mongo = SilpyMongoClient()
        self.parser = SenadoresParser()
        self.browser = webdriver.Firefox()
        self.browser.get("http://www.senado.gov.py/")

    def make_webdriver_wait(self, by, waited_element):
        try:
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.presence_of_element_located((by, waited_element)))
            print "Page is ready! Loaded: " + waited_element
        
        except TimeoutException:
            print "Loading took too much time!"

    def obtener_lista_de_senadores(self):
        url = base_url +  "index.php/senado/nomina/nomina-alfabetica"
        self.browser.get(url)        
        data = self.browser.page_source
        senadores =  parser.parse_senator_list(data)
        self.mongo.update_senadores(senadores)
        return senadores

    def _wait_document_ready(self, something):
        print something
        is_complete = self.browser.execute_script("return document.readyState;")
        if ( is_complete == "complete"):
            return True
        
    def obtener_info_de_senador(self, id):
        url="http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=%s" %(id)
        #url_proyectos = base_url + "index.php/lista-de-curriculum/68-curriculum?id_parla=%s#2-3-proyectos-presentados" %(id)
    
        self.browser.get(url)
        self.make_webdriver_wait(By.CLASS_NAME, "IN-widget")
        data = self.browser.page_source
        #TODO: extract comisiones
        committees = self.parser.parse_senator_committees(data)
        #TODO: extract dictamenes
        dictamenes = self.parser.parse_dictamenes(data)
        # self.browser.get(url_proyectos)
        # self.make_webdriver_wait(By.CLASS_NAME, "IN-widget")
        # wait = WebDriverWait(self.browser, 15)
        # wait.until(self._wait_document_ready, "Loaded")
        #data = self.browser.page_source
        
        proyectos = self.parser.parse_senator_presented_projects(data)
        result = self.mongo.update_senador({'id':id, 'proyectos': proyectos,
                                            'committees': committees,
                                            'dictamenes': dictamenes})
        print result

    def extract_senators_data(self):
        senadores = self.obtener_lista_de_senadores()
        for s in senadores:
            self.obtener_info_de_senador(s['id'])
                                
    def obtener_dictamenes_de_senador(self, id):
        #id_parla
        #los dictamenes de cada senador se cargan al llamar al tab de dictamenes
        url = 'http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100056#2-6-dict%C3%A1menes'


parser = SenadoresParser()
scrapper = SenadoresScrapper()
# scrapper.obtener_lista_de_senadores()
scrapper.extract_senators_data()
#obtener la lista de la base de datos y llamar al siguiente metodo
#html = read_file_as_string('resources/senadores/actividad_legislativa.html')
