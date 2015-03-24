'''
Created on Feb 26, 2015

@author: demian
'''

import httplib
import json
import urllib
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

application_x_www_form_urlencoded='application/x-www-form-urlencoded'
headers = {}
headers['Content-Type'] = application_x_www_form_urlencoded
headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
host= 'sil2py.senado.gov.py'
base_url = 'http://sil2py.senado.gov.py/'
port= 80

class SilpyScrapper(object):
    """
    Naviagation Flow for 
    """
    
    def __init__(self):
        self.headers = headers

    def _extract_response_headers(self, headers):
        """ recieves a tuple """
        headers_dict = {}
        for header in headers:
            if 'Date' in header:
                headers_dict['Date'] = header[header.index(":") : len(header)]
            else:
                key, val = header.split(":")
                headers_dict[key] = val

        return headers_dict

    def _extract_parlamentary_ids(self, html):
        """parlamentary id are contained on the images
           in the form of images/<id>.jpg
           returns a list of ids 
        """
    # TEST CODE #
        html = ''
        listarParlamentario = open('resources/lista_parlamentarios.html')
        for l in listarParlamentario:
            html +=l 
    # END TEST CODE #
        ids = []
        soup = BeautifulSoup(html)
        all_img = soup.find_all('img')
        str_images = '/images'
        
        for img in all_img:
            src = img['src']
            if str_images in src:
                ids.append(src[len(str_images)+1: len(src)].replace('.jpg',''))

        return ids

    def _create_connection(self):
        #conn = httplib.HTTPSConnection(host, port)
        conn = httplib.HTTPConnection(host, port)
        conn.debuglevel = 5
        conn.connect()
        return conn

    def execute_REST_call(self, method, url, content, headers, content_type):
        conn = self._create_connection()
        #default application/json
        if(content_type != None): headers['Content-Type'] = content_type    
        request = conn.request(method, base_url + url, content, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data

    def download_attachment(self):
        #TODO:
        # content = 'formMain=formMain&formMain%3AdataTableDetalle%3A0%3Aj_idt178=&javax.faces.ViewState=-3644735490815418626%3A-2324997477277913544'
        # return self._execute_REST_call('POST', '/formulario/VerDetalleTramitacion.pmf', content, headers, application_x_www_form_urlencoded)
        pass
        
    def get_session_values(self):
        #TODO: validate reponse status (decorate?)
        response, data = self._execute_REST_call('GET', '/main.pmf', None, headers, application_x_www_form_urlencoded)
        self.headers = self._extract_response_headers(response.msg.headers)

        #TODO: this section should go in a different method
        # viewStates are the way the server knows what is being asked
        # and what to respond, for different widgets there are different
        # viewStates
        soup = BeautifulSoup(data)
        input = soup.find(id='javax.faces.ViewState')
        self.viewState =  input['value']

        return response, data
        
    def get_parlamentary_details(self, parlamentary_id):
        parlamentary_id = '100064'
        _url = 'verProyectosParlamentario.pmf?q=verProyectosParlamentario%2F'+ parlamentary_id
        self._execute_REST_call('GET', '/formulario/ListarParlamentario.pmf', None, self.headers, application_x_www_form_urlencoded)
        
    def get_parlamentary_list(self, origin):
        """returns the list of parlamentraries for the period 2008-2013
           @origin: S=senadores, D=diputados """
        #TODO extract ids for periods superior to 2008-2013 if possible
        period = "100383" #2008-2013

        data = "javax.faces.partial.ajax=true&javax.faces.source=formMain:cmdBuscarParlamentario"\
               +"&javax.faces.partial.execute=@all"\
               +"&javax.faces.partial.render=formMain&formMain:cmdBuscarParlamentario=formMain:cmdBuscarParlamentario"\
               +"&formMain=formMain&formMain:idOrigen_input=" + origin + "&formMain:idPeriodoLegislativo_input=" + period \
               +"&javax.faces.ViewState=" + self.viewState 
                
        return self._execute_REST_call('POST', 'main.pmf', data, self.headers, application_x_www_form_urlencoded)

        
scraper = SilpyScrapper()
response, data = scraper.get_session_values()
response, data = scraper.get_parlamentary_list('S')
print "###########################################################################"
print response
print "###########################################################################"
print "\n"
print data
print "###########################################################################"

