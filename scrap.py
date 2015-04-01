'''
Created on Feb 26, 2015

@author: demian
'''

import httplib
import json
import urllib
import unicodedata
from bs4 import BeautifulSoup, CData
from HTMLParser import HTMLParser

import xml.etree.ElementTree as ET

application_x_www_form_urlencoded='application/x-www-form-urlencoded'
headers = {}
headers['Content-Type'] = application_x_www_form_urlencoded
headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'
#
#we are tunneling connection through ssh
# tunneling command (must have a valid connection, user on the server side)
#ssh -L 9999:silpy.congreso.gov.py:80 devel -N
#

host= 'sil2py.senado.gov.py'
base_url = 'http://sil2py.senado.gov.py'
# host= "localhost"
# base_url = "http://localhost:9999"
port= 80


class SilpyScrapper(object):
    """
    Naviagation Flow for 
    """
    
    def __init__(self):
        self.headers = headers
        
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

    def _extract_response_headers(self, headers):
        """ recieves a tuple """
        headers_dict = {}
        set_cookie = 'Set-Cookie'
        for header in headers:
            if 'Date' in header:
                #headers_dict['Date'] = header[header.index(":") : len(header)]
                pass
            else:
                key, val = header.split(":")
                headers_dict[key.strip()] = val.strip()
        return headers_dict
    
    @DeprecationWarning
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
    def _download_attachment(self):
        #TODO:
        # content = 'formMain=formMain&formMain%3AdataTableDetalle%3A0%3Aj_idt178=&javax.faces.ViewState=-3644735490815418626%3A-2324997477277913544'
        # return self._execute_REST_call('POST', '/formulario/VerDetalleTramitacion.pmf', content, headers, application_x_www_form_urlencoded)
        pass
        
    def _extract_sesion_values(self, response, data):
        self.headers = self._extract_response_headers(response.msg.headers)

        #TODO: this section should go in a different method
        # viewStates are the way the server knows what is being asked
        # and what to respond, for different widgets there are different
        # viewStates
        soup = BeautifulSoup(data)
        input = soup.find(id='javax.faces.ViewState')
        self.viewState =  input['value']
        
    def _extract_parlamentary_data(self, html):
        #print html
        partial_soup = BeautifulSoup(html)
        cdata_contents = []
        for cd in partial_soup.findAll(text=True):
            if isinstance(cd, CData):
                cdata_contents.append(cd)
        table_section = cdata_contents[0]
        viewState = cdata_contents[1]
        
        soup = BeautifulSoup(table_section)
        tbody = soup.find(id="formMain:dataTable_data")
        tr_list = tbody.find_all("tr")
        rows = []
        row = {}
        str_images = '/images'
        for tr in tr_list:
            #this is a table, of course it has a fixed length
            #0 = row_id, incremental
            #1 = img (we extract the parlamentary id from the image name
            #2 = name
            #3 = committees: div with list of divs
            #4 = projects: link using the extracted id from (2)

            td_list = tr.find_all("td")
            row['index'] = td_list[0].text.strip()
            row['name'] = td_list[2].text.strip()
            row['projects'] = td_list[4].text.strip()
            row_index = int(row['index'])-1
            #extraction of parlamentary id
            src = td_list[1].div.img['src']
            if str_images in src:
                row['id'] = src[len(str_images)+1: len(src)].replace('.jpg','')

                #extraction of formMain
                lis = td_list[3].div.div.find_all("li")
                committees = []
                for li in lis:
                    committee = {'text': li.text.strip(), 'formMain': li.a['id']}
                    formMain = committee['formMain']+ '=' + committee['formMain']
                    #viewState = self.viewState # "-3644735490815418626%3A-2324997477277913544"
                    body = 'javax.faces.ViewState='+ viewState + '&' + formMain
                    print (committee['text'], body)
                    committees.append(committee)

                    row['committees'] = committees

                    print row['index'] + " - " + row['name'] +" - " + row['id']
                    print "##################################################################"


    def init_session_values(self):
        #TODO: validate reponse status (decorate?)
        response, data = self._execute_REST_call('GET', '/main.pmf', None, headers, application_x_www_form_urlencoded)
        self._extract_sesion_values(response, data)
        return response, data

    def _request_search_form(self):
        #TODO: go to search from
        #extract data from header
        # POST /formulario/ListarParlamentario.pmf HTTP/1.1
        # Host: silpy.congreso.gov.py
        # User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0
        # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
        # Accept-Language: en-US,en;q=0.5
        # Accept-Encoding: gzip, deflate
        # Referer: http://silpy.congreso.gov.py/formulario/ListarParlamentario.pmf
        # Cookie: JSESSIONID=f94420a4878514955d10d14e1fed
        # Connection: keep-alive
        # Content-Type: application/x-www-form-urlencoded
        # Content-Length: 262
        
        #body:
        # formPreference=formPreference&formPreference%3Aj_idt34_collapsed=false&formPreference%3Afont_size=14&formPreference%3AstatefulSwitcher_input=cupertino&javax.faces.ViewState=2882989232062241367%3A3937926510672718829&formPreference%3Aj_id16=formPreference%3Aj_id16
        headers = {}
        headers['Set-Cookie'] = self.headers['Set-Cookie']
        response, data = self._execute_REST_call('POST', '/formulario/ListarParlamentario.pmf', None, headers, application_x_www_form_urlencoded)
        self._extract_sesion_values(response, data)
        return response, data

    def get_parlamentary_list(self, origin):
        """returns the list of parlamentraries for the period 2008-2013
           @origin: S=senadores, D=diputados """

        self._request_search_form()
        #TODO extract ids for periods superior to 2008-2013 if possible
        period = "100383" #2008-2013
        headers = {}
        headers['Content-Type'] = application_x_www_form_urlencoded
        headers["Accept"] = "application/xml, text/xml, */*; q=0.01"
        headers['Cookie'] = self.headers['Set-Cookie']
        headers['Referer'] = "http://silpy.congreso.gov.py/mani.pmf"
        headers['Faces-Request'] = "partial/ajax"
        headers['X-Requested-With'] =  "XMLHttpRequest"
        #headers[' Content-Length'] = "375"
        #headers['Cookie: JSESSIONID=593c27ecb57cd585a2a6099c9fb2
        headers['Connection'] = "keep-alive"
        headers['Pragma'] = "no-cache"
        headers['Cache-Control'] = "no-cache"

        #THIS WORKS
        data = "javax.faces.partial.ajax=true&javax.faces.source=formMain:cmdBuscarParlamentario"\
               +"&javax.faces.partial.execute=@all"\
               +"&javax.faces.partial.render=formMain&formMain:cmdBuscarParlamentario=formMain:cmdBuscarParlamentario"\
               +"&formMain=formMain&formMain:idOrigen_input=" + origin + "&formMain:idPeriodoLegislativo_input=" + period \
               +"&javax.faces.ViewState=" + self.viewState 

        # data = "javax.faces.partial.ajax%3Dtrue%26javax.faces.source%3DformMain%3AcmdBuscarParlamentario%26javax.faces.partial.execute%3D%40all%26javax.faces.partial.render%3DformMain%26formMain%3AcmdBuscarParlamentario%3DformMain%3AcmdBuscarParlamentario%26formMain%3DformMain%26formMain%3AidOrigen_input%3D"  + origin + "%26formMain%3AidPeriodoLegislativo_input%3D"+ period + "%26javax.faces.ViewState%3D" + self.viewState
        
        _url = '/formulario/ListarParlamentario.pmf'
        return self._execute_REST_call('POST', _url, data, headers, application_x_www_form_urlencoded)
    
    def get_presented_projects(self, parlamentary_id):
        """ver proyectos presentados"""
        #TODO
        parlamentary_id = '100064'
        _url = '/verProyectosParlamentario.pmf?q=verProyectosParlamentario%2F'+ parlamentary_id
        self._execute_REST_call('GET', _url, None, self.headers, application_x_www_form_urlencoded)
        
    def _extract_integrated_committees(self):
        pass

    def _extract_appointments(self):
        pass

        
scrapper = SilpyScrapper()
response, data = scrapper.init_session_values()
response, data = scrapper.get_parlamentary_list('D')
scrapper._extract_parlamentary_data(data)
#print data


update_data = 'resources/buscar_parlamentarios_update.html'
lista_parlamentarios = 'resources/lista_parlamentarios.html'

html = ''
htmlfile = open(lista_parlamentarios)
for l in htmlfile:
    html +=l 
#print html

#scrapper._extract_parlamentary_data(html)


#print table_section.find("formMain:dataTable_data")
#soup2 = BeautifulSoup(table_section)
#tbody = soup2.find(id="formMain:dataTable_data")

#_extract_parlamentary_data(table_section, "-3644735490815418626%3A-2324997477277913544")

# def _updated_viewState(html):
#     soup = BeautifulSoup(html)
#     #soup.find('partial-response')
#     updates = soup.find_all('update')
#     if updates != None and len(updates) > 0:
#         print updates[1].text

# _updated_viewState(html)


