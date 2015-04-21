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

    def __init__(self):
        path = 'resources/senadores/'
        self.nomina_html = read_file_as_string(path + 'lista.html')
        self.actividad = read_file_as_string(path + 'actividad_legislativa.html')
        self.dictamenes = read_file_as_string(path + 'dictamenes.html')
        
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
                            'name': name, 
                            'link': href,
                            'party': td_list[1].text,
                            'phone': td_list[2].text,
                            'email': td_list[3].a['href'].replace('mailto:', '')}
                senators.append(senator)

        return senators
        
    def parese_senator_info(self, id):
        #TODO: split this section into many?
        projects = []
        soup = BeautifulSoup(self.actividad)
        cv = soup.find(id = '2-1-curriculum-vitae')#save as chunk of data?
        table2  = soup.find('table', {'class': 'table2'})
        table_projects = soup.find(id = '2-3-proyectos-presentados')
        tr_list = table_projects.find_all('tr')
        tr_list = tr_list[1 : len(tr_list)] #remove header

        for tr in tr_list:
           # project_td = pr.find_all('td')
            td_list = tr.find_all('td')
            project = {}
            date_text = td_list[0].text
            project['date'] = date_text[: date_text.index('.'):-1].strip()[::-1]
            project['folder'] = td_list[1].text.strip()
            project_column = td_list[2].text
            project['name'] = project_column[:project_column.index('\n')]
            project['details'] = project_column[ :project_column.index('\n'): -1][::-1].strip()
            projects.append(project)
 
        return projects

    def parse_senator_committees(self):      
        soup = BeautifulSoup(self.actividad)
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


    def parse_dictamenes(self):
        soup = BeautifulSoup(self.dictamenes)
        dictamenes = soup.find(id = u'2-6-dictámenes')#be ware of the á
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

class SenadoresScrapper(object):

    def __init__(self):
        self.parser = SenadoresParser()
        self.browser = webdriver.Firefox()
        self.browser.get("http://www.senado.gov.py/")

    def obtener_lista_de_senadores(self):
        print "obteniendo lista de senadores"
        url = base_url +  "index.php/senado/nomina/nomina-alfabetica"
        self.browser.get(url)
        
        return self.browser.page_source
        
    def obtener_info_de_senador(self, id):
        url="http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100044"
        url_proyectos = "http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100044#2-3-proyectos-presentados"
        
    def obtener_dictamenes_de_senador(self, id):
        #id_parla
        #los dictamenes de cada senador se cargan al llamar al tab de dictamenes
        url = 'http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100056#2-6-dict%C3%A1menes'



from mongo_db import SilpyClient

mongo = SilpyClient()
parser = SenadoresParser()
scrapper = SenadoresScrapper()
data = scrapper.obtener_lista_de_senadores()
senadores =  parser.parse_senator_list(data)
mongo.save_senadores(senadores)

