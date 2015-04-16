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

from request_content import committee_item_data

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

import hashlib 

def write_html(html):

    name = "error/" + hashlib.sha224(html).hexdigest()+".html"
    f = open(name, "w")
    f.write(html)
    f.flush()
    f.close()
    

import functools
class updateViewState(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        self.clss = args[0]
        html = ''
        try:
            html =  kwargs['html']
        except:
            raise Exception("The decorated method must be invoked with an 'html' named parameter.")

        self._updated_viewState(html)
        self.f(*args, **kwargs)
            
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def _updated_viewState(self, html):
        #viewStates might be embbedded inside <input> or <update> 
        #and it changes according to the navigation
        soup = BeautifulSoup(html)
        viewState_container = soup.find(id="javax.faces.ViewState")
        viewState = None
        if viewState_container.name == 'input': 
            viewState = viewState_container['value']
        elif viewState_container.name == 'update':
            viewstate = viewState_container.text 
        
        if self.clss.viewState != viewState:
            print "replacing viewstates: oldval: " + self.clss.viewState + ' | newval: ' +viewState
            self.clss.viewState = viewState


class SilpyHTMLParser(object):

##################################
# HTML Parser Section
#
# As for now rest call code and html parsing ar too mixed, 
# refactoring needed 
##################################
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
          
    def _extract_parlamentary_data(self, html):
        #TODO:extract designaciones 
        #http://silpy.congreso.gov.py/formulario/VerDetalleTramitacion.pmf?q=VerDetalleTramitacionVerDetalleTramitacion%2F101470
        partial_soup = BeautifulSoup(html)
    #    cdata_contents = []
    #        widgets updates come insade a CDATA
        # for cd in partial_soup.findAll(text=True):
        #     if isinstance(cd, CData):
        #         cdata_contents.append(cd)
        # table_section = cdata_contents[0]
        # viewState = cdata_contents[1]
        
        soup = BeautifulSoup(html)
        tbody = soup.find(id="formMain:dataTable_data")

        tr_list = tbody.find_all("tr")
        rows = []
        str_images = '/images'
        for tr in tr_list:
            #this is a table, of course it has a fixed length
            #0 = row_id, incremental
            #1 = img (we extract the MP id from the image name
            #2 = name
            #3 = committees: div with list of divs
            #4 = projects: link using the extracted id from (2)
            row = {}
            td_list = tr.find_all("td")
            row['index'] = td_list[0].text.strip()
            row['name'] = td_list[2].text.strip()
            row['projects_body_param'] = td_list[4].text.strip() #parameter to invoke projects 
            row_index = int(row['index'])-1
            #extraction of MP id
            src = td_list[1].div.img['src']
            if str_images in src:
                #TODO: download img!
                row['id'] = src[len(str_images)+1: len(src)].replace('.jpg','')
                #extraction of formMain
                #formMain goes in the following request to get
                # committee details  list_projects_by_committee(body_param)
                lis = td_list[3].div.div.find_all("li")
                committees = []
                for li in lis:
                    #TODO: extract js from anchor
                    # formMain = li.a['id']
                    # formMain2 = formMain + '=' + formMain
                    # appended_string = 'javax.faces.ViewState='+ viewState + '&' + formMain2
                    js_call = li.a['onclick']
                    committee = {'text': li.text.strip(), 'js_call': js_call}               
                    committees.append(committee)
                row['committees'] = committees
                    
            rows.append(row)
        return rows

    def _extract_statistics_table(self, html):
        #extracts data from the statistics table in resources/projects_by_committee.html
        soup = BeautifulSoup(html)
        committee_table = soup.find(id="formMain:panelComision")
        committee = committee_table.tr.td.text
        status = committee[committee.index('[')+1 : committee.index(']')]
        statistics_div = soup.find(id="formMain:j_idt85")
        #th_list = statistics_div.table.thead.find_all("th")
        statistics = []
        if statistics_div:
            tr_list = statistics_div.table.tbody.find_all("tr")
            statistics = []
            for tr in tr_list:
                td_list = tr.find_all("td")
                values = {}
                values["cantidad"] = td_list[0].text
                values["estado"] = td_list[1].text 
                statistics.append(values)
        else:
            write_html(html)
  
        return statistics

    def _extract_projects_by_committee(self, html):
        #extracts data from the results table in resources/projects_by_committee.html
        soup = BeautifulSoup(html)
        result_tbody = soup.find(id = "formMain:dataTable_data")
        tr_list = result_tbody.find_all("tr")
       
        projects = []
        #TODO: set this as header
        description = soup.find(id="formMain:denominacion")

        for tr in tr_list:
            td_list = tr.find_all("td")

            if td_list != None and len(td_list) > 0:
                project = {}
                td0 = td_list[0]
                #td2 = td_list[2] #votacion??
                if td0.div == None:
                   write_html(html)

                if td0.div != None:
                    project['description'] = td0.a.text
                    project['data'] = td0.a['id'] #dont remember what this is

                span_list = td0.find_all('span')

                if span_list != None and len(span_list) > 0:
                    project['title'] = span_list[0].text.strip()
                    texts_rows = span_list[1].text.split('\n')
                    if len(texts_rows) > 1:#sometimes there are just counted comments

                        entry_date, date = texts_rows[1].split(":")
                        folder, id = texts_rows[3].split(":")
                        project['ingreso'] = date.strip()
                        project['expediente'] = id.strip()

                        if len(texts_rows) >= 3: #there is also a mensaje section, and other
                            subtable = span_list[1].table #texts_rows, len(texts_rows)
                            trs = subtable.find_all("tr")
                            for tr in trs:
                                tr_spans = tr.find_all('span')
                                if len(tr_spans) > 0:
                                    messages = []
                                    for span in tr_spans:
                                        messages.append(span.text.replace("|", "").strip())
                                    project['messages'] = messages

                if len(td_list) > 3:
                    td3 = td_list[3]
                    td3_span_list = td3.find_all('span')
                    for span in td3_span_list:
                        span.text
                    if len(td3_span_list) > 2:
                        project['stage'] = {'camara': td3_span_list[0].text, td3_span_list[1].text : td3_span_list[2].text} 
                if len(project) != 0:        
                    projects.append(project)
        
        return projects

    def number_of_rows_found(self, html):
        #number of rows
        soup = BeautifulSoup(html)
        #print soup.find(id='formMain:dataTable')
        th = soup.find('th', {'class':"ui-datatable-header ui-widget-header"}) 
        text = th.table.tbody.tr.td.text
        number_of_rows = text[0 : text.index('registros recuperados')]
        return int(number_of_rows.strip())

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class SilpyScrapper(object):
    """
    Naviagation Flow for 
    """

    def __init__(self):
        self.parser = SilpyHTMLParser()
        self.browser = webdriver.Firefox()
        self.browser.get("http://silpy.congreso.gov.py/main.pmf")
                               
    def make_webdriver_wait(self, by, waited_element):
        try:
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.presence_of_element_located((by, waited_element)))
            print "Page is ready! Loaded: " + waited_element
        
        except TimeoutException:
            print "Loading took too much time!"

    def list_projects_by_committee(self, data):
        #TODO
        return browser.page_source

    def get_parlamentary_list(self, origin):
        """returns the list of parlamentraries for the period 2008-2013
           @origin: S=senadores, D=diputados """

        input = self.browser.find_element_by_id("formPreference:j_id16")
        input.click()

        self.make_webdriver_wait(By.ID, "formMain:idPeriodoLegislativo_input")
        select_periodo = self.browser.find_element_by_id("formMain:idPeriodoLegislativo_input")

        select = Select(select_periodo)
        select.select_by_index(4)
        self.browser.execute_script("PrimeFaces.ab({source:'formMain:cmdBuscarParlamentario',update:'formMain'});return false;")
        
        # wait for th class? Yes
        self.make_webdriver_wait(By.CSS_SELECTOR, '.ui-widget-content.ui-datatable-even')#".ui-datatable-header.ui-widget-header")
        
        number_of_rows = parser.number_of_rows_found(self.browser.page_source)

        #wait for something related to the data table
        #for instance the last row id
        # formMain:dataTable:43:j_idt92 -> formMain:dataTable:%s:j_idt92 %(str(number_of_rows - 1))
        last_row_id = "formMain:dataTable:%s:j_idt92" %(str(number_of_rows - 1))
        print "now we wait for " + last_row_id
        self.make_webdriver_wait(By.ID, last_row_id)
#       self.make_webdriver_wait('formMain:dataTable:j_idt89')
        return self.browser.page_source 

        
    def get_presented_projects(self, parlamentary_id):
        """ver proyectos presentados"""
        #TODO
        #parlamentary_id = '100064'
        _url = '/verProyectosParlamentario.pmf?q=verProyectosParlamentario%2F'+ parlamentary_id
        self._execute_REST_call('GET', _url, None, self.headers, application_x_www_form_urlencoded)
        
    def process_projects_by_committee(self, body_param):
        #TODO: discover which list is shown: "en estudio" o "dictaminados"
        # invoke the alternate list and call this method again
        #
        response, data = self.list_projects_by_committee(body_param)
        #soup = BeautifulSoup(data)
        stats = self._extract_statistics_table(html=data)
        projects = self._extract_projects_by_committee(html=data)
        return stats, projects




#######################
### MainApp Section ###
#######################
from mongo_db import SilpyClient
parser = SilpyHTMLParser()
scrapper = SilpyScrapper()
sc = SilpyClient()

data = scrapper.get_parlamentary_list('D')
rows = parser._extract_parlamentary_data(data)

result = sc.save_projects(rows)
print result

# from db import Session, Parlamentario, Camara
# session = Session()
# camara_diputados = Camara(id=1, nombre='Diputados', periodo='2013-2018')
# camara_senadors = Camara(id=2, nombre='Senadores', periodo='2013-2018')
# for r in rows:
#     #parlamentario = Parlamentario(id=r['id'], nombre=r['name'])
#     #parlamentario.camaras = [camara_diputados]
#     committees = r['committees']
#     print r['name']

#     for c in committees:
#         appended_string = c['body_param']
#         body_param = committee_item_data + appended_string        
#         stats, projects = scrapper.process_projects_by_committee(body_param)        

#     session.add(parlamentario)
# session.commit()


# update_data = 'resources/buscar_parlamentarios_update.html'
#lista_parlamentarios = 'resources/lista_parlamentarios.html'
# projects_by_committee = 'resources/projects_by_committee.html'

# html = ''
# htmlfile = open(lista_parlamentarios)

# for l in htmlfile:
#     html +=l

# #number of rows
# rows = parser._extract_parlamentary_data(html)

# print rows
