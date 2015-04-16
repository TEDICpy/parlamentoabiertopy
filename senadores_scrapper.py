#In this file we process data comming from
#http://www.senado.gov.py
#TODO:

import httplib
import json
import urllib
import unicodedata
from bs4 import BeautifulSoup

class SenadoresParser(object):
    pass



class SenadoresScrapper(object):

    def _create_connection(self):
        #conn = httplib.HTTPSConnection(host, port)
        conn = httplib.HTTPConnection(host, port)
        conn.debuglevel = 5
        conn.connect()
        return conn

    def _execute_REST_call(self, method, url, content, headers, content_type):
        conn = self._create_connection()
        #default application/json
        if(content_type != None): headers['Content-Type'] = content_type    
        request = conn.request(method, base_url + url, content, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data


    def obtener_lista_de_senadores(self):
        url = "www.senado.gov.py/index.php/senado/nomina/nomina-alfabetica"
        

    def obtener_info_de_senador(self, id):
        url="http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100044"
        url_proyectos = "http://www.senado.gov.py/index.php/lista-de-curriculum/68-curriculum?id_parla=100044#2-3-proyectos-presentados"
        
