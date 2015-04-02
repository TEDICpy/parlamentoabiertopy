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


class SilpyScrapper(object):
    """
    Naviagation Flow for 
    """
    
    def __init__(self):
        self.headers = headers
        
    def _create_connection(self):
        #conn = httplib.HTTPSConnection(host, port)
        conn = httplib.HTTPConnection(host, port)
        conn.debuglevel = 0
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
        partial_soup = BeautifulSoup(html)
        cdata_contents = []
        #widgets updates come insade a CDATA
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
                    appended_string = 'javax.faces.ViewState='+ viewState + '&' + formMain
                    #print (committee['text'], appended_string)
                    committees.append(committee)
                    row['committees'] = committees
                    #download data                    
                    body = committee_item_data + appended_string
                    response, data = self.list_projects_by_committee(body)
                    
                    #
                    #TODO: improve calls, handle response
                    #
                    print data
                    #print row['index'] + " - " + row['name'] +" - " + row['id']
                    #print "##################################################################"
                    

    def list_projects_by_committee(self, data):
        headers = {}
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers['Cookie'] = self.headers['Set-Cookie']
        headers['Referer'] = "http://silpy.congreso.gov.py/main.pmf"
        _url = '/formulario/ListarParlamentario.pmf'        
        return self._execute_REST_call('POST', _url, data, headers, application_x_www_form_urlencoded)

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
        headers['Referer'] = "http://silpy.congreso.gov.py/main.pmf"
        headers['Faces-Request'] = "partial/ajax"
        headers['X-Requested-With'] =  "XMLHttpRequest"
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
        response, data = self._execute_REST_call('POST', _url, data, headers, application_x_www_form_urlencoded)
#        self._extract_sesion_values(response, data)
        return response, data
    
    def get_presented_projects(self, parlamentary_id):
        """ver proyectos presentados"""
        #TODO
        #parlamentary_id = '100064'
        _url = '/verProyectosParlamentario.pmf?q=verProyectosParlamentario%2F'+ parlamentary_id
        self._execute_REST_call('GET', _url, None, self.headers, application_x_www_form_urlencoded)
        
    def projects_by_committee_extractor(self, html):
        #TODO: discover which list is shown: "en estudio" o "dictaminados"
        # invoke the alternate list and call this method again
        stats = self._extract_statistics_table(html)
        projects = self._extract_projects_by_committee(html)
        return stats, projects

    def _extract_statistics_table(self, html):
        #extracts data from the statistics table in resources/projects_by_committee.html
        soup = BeautifulSoup(html)
        committee_table = soup.find(id="formMain:panelComision")
        committee = committee_table.tr.td.text
        status = committee[committee.index('[')+1 : committee.index(']')]
        statistics_div = soup.find(id="formMain:j_idt85")
        #th_list = statistics_div.table.thead.find_all("th")
        tr_list = statistics_div.table.tbody.find_all("tr")
        statistics = []
        for tr in tr_list:
            td_list = tr.find_all("td")
            values = {}
            values["cantidad"] = td_list[0].text
            values["estado"] = td_list[1].text 
            statistics.append(values)

        return statistics
        
    def _extract_projects_by_committee(self, html):
        #extracts data from the results table in resources/projects_by_committee.html
        soup = BeautifulSoup(html)
        result_tbody = soup.find(id = "formMain:dataTable_data")
        tr_list = result_tbody.find_all("tr")
        projects = []
        for tr in tr_list:
            td_list = tr.find_all("td")

            if td_list != None and len(td_list) > 0:
                project = {}
                td0 = td_list[0]
                #td2 = td_list[2] #votacion??
                if td0.div != None:
                    project['description'] = td0.a.text
                    project['data'] = td0.a['id']

                span_list = td0.find_all('span')

                if span_list != None and len(span_list) > 0:
                    project['title'] = span_list[0].text.strip()
                    texts_rows = span_list[1].text.split('\n')
                    if len(texts_rows) > 1:#sometimes there are just counted comments

                        entry_date, date = texts_rows[1].split(":")
                        folder, id = texts_rows[3].split(":")
                        project['ingreso'] = date.strip()
                        project['expediente'] = id.strip()

                        if len(texts_rows) >= 3: #there is also mensaje section
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



scrapper = SilpyScrapper()
# response, data = scrapper.init_session_values()
# response, data = scrapper.get_parlamentary_list('D')
# scrapper._extract_parlamentary_data(data)
#print data

update_data = 'resources/buscar_parlamentarios_update.html'
lista_parlamentarios = 'resources/lista_parlamentarios.html'
projects_by_committee = 'resources/projects_by_committee.html'

html = ''
htmlfile = open(projects_by_committee)
for l in htmlfile:
    html +=l 

print scrapper.projects_by_committee_extractor(html)
 

#def  _updated_viewState(html):
#     soup = BeautifulSoup(html)
#     #soup.find('partial-response')
#     updates = soup.find_all('update')
#     if updates != None and len(updates) > 0:
#         print updates[1].text

# _updated_viewState(html)


