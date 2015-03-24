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

class SilpyHtmlParser(HTMLParser):
                                
    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
            
    def handle_data(self, data):
        print "Encountered some data  :", data

            
class SilpyScrapper(object):

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

    def create_connection(self):
        #conn = httplib.HTTPSConnection(host, port)
        conn = httplib.HTTPConnection(host, port)
        conn.debuglevel = 5
        conn.connect()
        return conn

    def execute_REST_call(self, method, url, content, headers, content_type):
        conn = self.create_connection()
        #default application/json
        if(content_type != None): headers['Content-Type'] = content_type    
        request = conn.request(method, base_url + url, content, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data

    def download_attachment(self):
        content = 'formMain=formMain&formMain%3AdataTableDetalle%3A0%3Aj_idt178=&javax.faces.ViewState=-3644735490815418626%3A-2324997477277913544'
        return self.execute_REST_call('POST', '/formulario/VerDetalleTramitacion.pmf', content, headers, application_x_www_form_urlencoded)

    def get_session_values(self):
        #TODO: validate reponse status (decorate?)
        
        response, data = self.execute_REST_call('GET', '/main.pmf', None, headers, application_x_www_form_urlencoded)
        self.headers = _extract_response_headers(response.msg.headers)

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
        self.execute_REST_call('GET', '/formulario/ListarParlamentario.pmf', None, self.headers, application_x_www_form_urlencoded)
        
    def get_parlamentary_list(self, origin):
        """returns the list of parlamentraries for the period 2008-2013"""
        #TODO extract ids for periods superior to 2008-2013 if possible
        origin = "S"# S=senadores, D=diputados
        period = "100383" #2008-2013

        print "viewstate: "+self.viewState
        data = "javax.faces.partial.ajax=true&javax.faces.source=formMain:cmdBuscarParlamentario"\
               +"&javax.faces.partial.execute=@all"\
               +"&javax.faces.partial.render=formMain&formMain:cmdBuscarParlamentario=formMain:cmdBuscarParlamentario"\
               +"&formMain=formMain&formMain:idOrigen_input=" + origin + "&formMain:idPeriodoLegislativo_input=" + period \
               +"&javax.faces.ViewState="+self.viewState #%(origin, period, self.viewState)
        
        # data = "javax.faces.partial.ajax=true&javax.faces.source=formMain%3AcmdBuscarParlamentario"\
        #     + "&javax.faces.partial.execute=%40all&javax.faces.partial.render="\
        #     + "formMain&formMain%3AcmdBuscarParlamentario=formMain%3AcmdBuscarParlamentario&formMain="\
        #     + "formMain&formMain%3AidOrigen_input=%s&formMain%3AidPeriodoLegislativo_input=%s&javax.faces.ViewState=%s" %(origin, period, self.viewState)

        print type(self.headers)
        #return self.execute_REST_call('POST', 'main.pmf', data, self.headers, application_x_www_form_urlencoded)

        
scrap = SilpyScrapper()
response, data = scrap.get_session_values()
#response, data = scrap.get_parlamentary_list('S')
print "###########################################################################"
print _extract_response_headers(headers)
print "###########################################################################"
print "\n"
#print data
print "###########################################################################"

#parser = SilpyHtmlParser()



listarParlamentario = open('lista_parlamentarios.html')
data = ''
for l in listarParlamentario:
    data +=l 

#main = open('main.html')
#mainHtml = ''
# for l in main:
#     mainHtml += l

# soup = BeautifulSoup(mainHtml)
# input = soup.find(id='javax.faces.ViewState')
# print input['value']

#las imagenes contienen el id del parlamentario
def extract_parlamentary_ids(html):
    soup = BeautifulSoup(html)
    all_img = soup.find_all('img')
    str_images = '/images'
    ids = []
    
    for img in all_img:
        src = img['src']
        if str_images in src:
            ids.append(src[len(str_images)+1: len(src)].replace('.jpg',''))
    return ids

#print extract_parlamentary_ids(data)

