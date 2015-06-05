#-*- coding: utf-8 -*-
'''
Created on Feb 26, 2015

@author: demian
'''

import httplib
import json
import urllib
import hashlib 
import utils
import requests
import unicodedata
from bs4 import BeautifulSoup, CData
from HTMLParser import HTMLParser
import time

from request_content import committee_item_data


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

    def extraer_items_menu(self, html):
        #retorna un diccionario con los
        #items del menu principal
        soup = BeautifulSoup(html)
        main_menu_form = soup.find(id='formPreference')
        menu_items = main_menu_form.find_all('li')
        menu = {}
        for i in menu_items:
            anchor = i.a
            if anchor != None:
                menu[i.text] = i.a['onclick']
        return menu
          
    def parse_parlamentary_data(self, html):
        #TODO:extract designaciones 
        #http://silpy.congreso.gov.py/formulario/VerDetalleTramitacion.pmf?q=VerDetalleTramitacionVerDetalleTramitacion%2F101470
        partial_soup = BeautifulSoup(html)
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
                #http://sil2py.senado.gov.py/images/100081.jpg
                row['img'] = 'http://sil2py.senado.gov.py'+src
                row['id'] = src[len(str_images)+1: len(src)].replace('.jpg','')
                #extraction of formMain
                #formMain goes in the following request to get
                # committee details  list_projects_by_committee(body_param)
                #lis = td_list[3].div.div.find_all("li")
                #work_div contains two subdivs, one for projects and the other 
                #for designations 
                work_divs = td_list[3].div.find_all('div', recursive=False)
                committees_lis = work_divs[0].find_all("li")
                committees = []
                for li in committees_lis:
                    js_call = li.a['onclick']
                    committee = {'text': li.text.strip(), 'js_call': js_call}
                    committees.append(committee)
                row['committees'] = committees
                #designation extraction
                #apparently not all rows have a designations div
                if len(work_divs) > 1:
                    designation_lis = work_divs[1].find_all("li")
                    designations = []
                    for li in designation_lis:                         
                        js_call = li.a['onclick']
                        designation = {'text': li.text.strip(), 'js_call': js_call}
                        designations.append(designation)
                    row['designations'] = designations
            rows.append(row)
            
        return rows

    def parse_projects_by_parlamentary(self, html):
        soup = BeautifulSoup(html)
        #this tbody contains the actual data from the html comming from
        #http://sil2py.senado.gov.py/formulario/verProyectosParlamentario.pmf?q=verProyectosParlamentario%2F100081
        #the id increments for each section
        #TODO: count sections?
        projects = []
        #ids are generated dynamically
        #so wi search for the div with attr=role and value=tablist
        #and extract its id
        content_id = soup.find(id='formMain').find_all('div', {'role': 'tablist'})[0]['id']
        tabs_div = soup.find(id=content_id)
        h3_list = tabs_div.find_all('h3', recursive=False)#number of tabs                         
       
        for i in range(0,len(h3_list)):
            id=content_id + ":%i:dataTable_data" %(i)
            tbody=soup.find(id=id)
            projects.append(self.parsear_lista_de_proyectos(tbody))
        return projects

    #quiza ni necesitamos ya que podemos quitar las estadisticas localmente
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
                values["quantity"] = td_list[0].text
                values["stage"] = td_list[1].text 
                statistics.append(values)
        else:
            write_html(html)
  
        return statistics

    def _extract_projects_by_committee(self, html):
        #extracts data from the results table in resources/projects_by_committee.html
        soup = BeautifulSoup(html)
        result_tbody = soup.find(id = "formMain:dataTable_data")
        tr_list = result_tbody.find_all("tr")
        #TODO: set this as header
        description = soup.find(id="formMain:denominacion")       
        return self.parsear_lista_de_proyectos(result_tbody)

    def parsear_lista_de_proyectos(self, result_tbody, id=None):
        #result_body is the tbody which contains the tebls's rows
        #Ex.: result_tbody = soup.find(id = "formMain:dataTableProyecto_data") 
        #if the id is not None then we extract the result_tbody with that id        
        if id is not None:
            result_tbody = result_tbody.find(id)
        
        tr_list = result_tbody.find_all("tr", recursive=False)
        projects = []
        
        for tr in tr_list:
            td_list = tr.find_all("td", recursive=False)            
            if td_list != None and len(td_list) > 0:
                project = {}
                td0 = td_list[0]

                if td0.div != None:
                    project['title'] = td0.a.text                   
                span_list = td0.find_all('span')
                if span_list != None and len(span_list) > 0:
                    project['type'] = span_list[0].text.strip()
                    texts_rows = span_list[1].text.split('\n')
                    #el id del proyecto se quita del icono "Votar Por Proyecto"
                    #siendo el id la ultima parte numerica del link.
                    #Ej: http://sil2py.senado.gov.py/votacion/VotarProyecto.pmf?q=votarProyecto%2F1112
                    #id=1112
                    # El link al detalle de tramitacion seria:
                    #silpy.congreso.gov.py/formulario/VerDetalleTramitacion.pmf?q=VerDetalleTramitacion%2F1112
                    subtables = span_list[1].find_all('table')
                    last_table = subtables[len(subtables) - 1] #la tabla con la imagen del tipito con el altoparlante
                    id = last_table.tbody.td.a['href'][::-1]
                    id = id[:id.index('%') - 2][::-1]
                    project['id'] = id
                    
                    if len(texts_rows) > 1:#sometimes there are just counted comments                     
                        entry_date, date = texts_rows[1].split(":")
                        folder, id = texts_rows[3].split(":")
                        project['entry_date'] = date.strip()
                        project['file'] = id.strip()                        
                        #eliminar o aumentar esta seccion
                        #hay mas elementos pero por ahi no son importantes
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

                #segunda columna: Etapa
                if len(td_list) >= 1:
                    td1 = td_list[1]
                    td1_span_list = td1.find_all('span')
                    #print "td1_span_list " + str(td1_span_list)
                    if len(td1_span_list) > 1:
                        project['estage'] = {'chamber': td1_span_list[0].text, 
                                             td1_span_list[1].text : td1_span_list[2].text} 

                if len(project) != 0:        
                    projects.append(project)

        return projects

    def parsear_lista_de_proyectos_dialog(html):
        #recibe el hmtl de la lista de sesiones
        #con el dialog de la lista de proyectos
        soup = BeautifulSoup(html)
        tbody = soup.find(id = 'formMain:dataTableProyecto_data')
        tr_list = tbody.find_all('tr')
        proyectos = self.parsear_lista_de_proyectos(tbody)
    
    def parsear_lista_sessiones(self, html):
        #recibe el html despues de buscar las sesiones por periodo 
        proyectos = []
        soup = BeautifulSoup(html)
        periodo = soup.find(id = 'formMain:idPeriodoParlamentario_label')
        periodo = periodo.text.strip()
        tbody = soup.find(id = 'formMain:dataTable_data')
        tr_list = tbody.find_all('tr')
        for tr in tr_list:
            td_list = tr.find_all('td')
            if len(td_list) > 0:
                proyecto = {}
                proyecto['index'] = td_list[0].text.strip()
                proyecto['fecha'] = td_list[1].div.text.strip()
                proyecto['nro_sesion'] = td_list[2].text.strip()
                proyecto['tipo_sesion'] = td_list[3].text.strip()
                proyecto['anexos_js_call'] = td_list[4].button['onclick']
                proyecto['verProyectos_js_call'] = td_list[5].button['onclick']
                proyectos.append(proyecto)
        return proyectos

    def extract_session_attachment(self, html):
        #anexos por de la sesion
        soup = BeautifulSoup(html)
        anexos_table = soup.find(id="formMain:dataTableDetalle").table
        tr_list = anexos_table.tbody.find_all('tr')
        anexos = []
        for tr in tr_list:
            td_list = tr.find_all('td')
            #td_list[0].text.strip() 
            nombre = td_list[1].text.strip()
            #discard size and replace spaces with underscore
            nombre = nombre[:nombre.find("\n")].replace(" ", "_")
            anexo = {'name': nombre,
                     'registered_date': td_list[2].text.strip(),
                     'button_id': td_list[3].button['id']}
            anexos.append(anexo)
        return anexos

    def extraer_comisiones_por_periodo(self, html):
        soup = BeautifulSoup(html)
        tbody = soup.find(id='formMain:dataTable_data')
        tr_list = tbody.find_all('tr', recursive=False)
        comisiones = []

        for tr in tr_list:
            comision = {}
            td_list = tr.find_all('td', recursive=False)
            comision['denominacion'] = td_list[1].text.strip()
            comision['type']  = td_list[2].text.strip()
            comision['chamber'] = td_list[3].text.strip()
            comision['member_js_call'] = td_list[4].div.button['onclick']
            comisiones.append(comision)
        return comisiones

    def extraccion_de_informacion_de_proyecto(self, html):
        soup = BeautifulSoup(html)
        info_div = soup.find(id='formMain:j_idt81_content')
        
        #informacion del proyecto
        info = {}
        info['file'] = info_div.find(id='formMain:expedienteCamara').text.strip()
        info['type'] = info_div.find(id='formMain:idTipoProyecto').text.strip()
        info['subject'] = info_div.find(id='formMain:idMateria').text.strip()
        info['importance'] = info_div.find(id='formMain:idUrgencia').text.strip()
        info['entry_date'] = info_div.find(id='formMain:fechaIngreso').text.strip()
        info['iniciativa'] = info_div.find(id='formMain:idTipoIniciativa').text.strip()
        info['origin'] = info_div.find(id='formMain:idOrigen').text.strip()
        info['message'] =info_div.find(id='formMain:numeroMensaje').text.strip()
        info['heading'] =info_div.find(id='formMain:acapite').text.strip()

        #'Etapa de la Tramitación'
        etapa = {}
        etapas_table = soup.find(id='formMain:panelEtapas')
        etapa['stage'] = etapas_table.find(id='formMain:idEtapaProy').text.strip()
        etapa['sub_stage'] = etapas_table.find(id='formMain:idSubEtapaProy').text.strip()
        etapa['status'] = etapas_table.find(id='formMain:idEstadoProyecto').text.strip()

        #detalle de tramitacion
        tbody_content = soup.find(id='formMain:dataTableTramitacion_data')
        tr_list = tbody_content.find_all('tr', recursive=False)

        tramitaciones = []
        for tr in tr_list:
            tramitacion = {}
            td_list = tr.find_all('td')
            tramitacion['index'] = td_list[0].text.strip()
            tramitacion['session'] = td_list[1].text.strip()
            tramitacion['date'] = td_list[2].text.strip()

            #TODO: extraccion de etapa se puede generalizar
            if len(td_list) >= 1:
                td1 = td_list[3]
                td1_span_list = td1.find_all('span')
                #print "td1_span_list " + str(td1_span_list)
                if len(td1_span_list) > 1:
                    tramitacion['stage'] = {'chamber': td1_span_list[0].text, 
                                            td1_span_list[1].text : td1_span_list[2].text} 

            #Resultado
            #TODO: todo esto es un kilombo, aqui hay de todo
            tramitacion['result'] = td_list[4]
            tramitaciones.append(tramitacion)

        return tramitaciones
       
    def extraer_miembros_por_comision(self, html):
        soup = BeautifulSoup(html)
        miembros_div = soup.find('div', {'class' : 'ui-datatable-scrollable-body'})
        tr_list =  miembros_div.table.find_all('tr')
        p = None
        for tr in tr_list:
            p = {}
            td_list = tr.find_all('td', recursive=False)
            reverse = td_list[0].img['src'][::-1]
            p['id'] = reverse[reverse.index('.'): reverse.index('/')][::-1]
            p['name'] = td_list[1].text.strip()
            p['chamber'] = td_list[2].text.strip()
            p['post'] = td_list[3].text.strip()
        return p

    def procesar_proyectos_por_comite(self, data):
        soup = BeautifulSoup(data)
        stats = self._extract_statistics_table(html=data)
        projects = self._extract_projects_by_committee(html=data)
        return stats, projects

    def number_of_rows_found(self, html):
        #numero de registros encontrados en la tabla
        #aparentemente se utiliza la misma clase css en diferentes tablas
        soup = BeautifulSoup(html)
        #print soup.find(id='formMain:dataTable')
        th = soup.find('th', {'class':"ui-datatable-header ui-widget-header"}) 
        text = th.table.tbody.tr.td.text
        number_of_rows = text[0 : text.index('registros recuperados')]
        return int(number_of_rows.strip())
    
    def extract_viewstate(self, html):
        soup = BeautifulSoup(html)
        viewState_container = soup.find(id="javax.faces.ViewState")
        viewState = None
        if viewState_container.name == 'input': 
            viewState = viewState_container['value']
        elif viewState_container.name == 'update':
            viewstate = viewState_container.text         
        return viewState


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class SilpyNavigator(object):
    """
    Naviagation Flow for 
    """

    def __init__(self, browser=None):
        self.parser = SilpyHTMLParser()
        if browser:
            self.browser=browser
        else:
            self.browser = utils.get_new_browser()
        self.browser.get("http://silpy.congreso.gov.py/main.pmf")
                               

    def close_driver(self):
       self.driver.close() 

    def make_webdriver_wait(self, by, waited_element):
        try:
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.presence_of_element_located((by, waited_element)))
            print "Page is ready! Loaded: " + waited_element
        
        except TimeoutException:
            print "Loading took too much time! for element: " + waited_element
            
    def _make_driver_wait(self):
        try:
            wait = WebDriverWait(self.browser, 15)
            wait.until(utils._wait_document_ready, self.browser)
        except TimeoutException:
            print "Loading took too much time!"
       
    def count_table_rows(self):
        #wait for css_element
        #TODO: css element as parameter
        css_element = ".ui-widget-content.ui-datatable-even"
        self.make_webdriver_wait(By.CSS_SELECTOR, css_element)
        return self.parser.number_of_rows_found(self.browser.page_source)
        
    def _call_menu_item(self, item_text):
        html = self.browser.page_source        
        menu = self.parser.extraer_items_menu(html)
        for key, val in menu.items():
            if key == item_text:
                js_call = val
                break
        if js_call:
            self.browser.execute_script(js_call)

    def get_parlamentary_list(self, origin):
        """returns the list of parlamentraries for the period 2008-2013
           @origin: S=senadores, D=diputados """
        #TODO: makte option selection with parameters
        #for origin and period
        self._call_menu_item(u'Parlamentarios por Período')#from side menu
        self.make_webdriver_wait(By.ID, "formPreference:j_id16")
        # input = self.browser.find_element_by_id("formPreference:j_id16")
        # input.click()
        self.make_webdriver_wait(By.ID, "formMain:idPeriodoLegislativo_input")
#        formMain:idOrigen_input
        select_camara_element = self.browser.find_element_by_id("formMain:idOrigen_input")
        select_camara = Select(select_camara_element)
        select_camara.select_by_value(origin)
        select_periodo = self.browser.find_element_by_id("formMain:idPeriodoLegislativo_input")
        select = Select(select_periodo)
        select.select_by_index(4)
        self.browser.execute_script("PrimeFaces.ab({source:'formMain:cmdBuscarParlamentario'" +\
                                    ",update:'formMain'});return false;")        
        # wait for th class? Yes
        #WARNING: this is a bug
        # the css class .ui-widget-content.ui-datatable-even can be even or odd depending on the number of rows
        #use 'data-ri' instead of css ?
        self.make_webdriver_wait(By.CSS_SELECTOR, '.ui-widget-content.ui-datatable-even')#".ui-datatable-header.ui-widget-header")
        number_of_rows = self.parser.number_of_rows_found(self.browser.page_source) #extraemos la cantidad de registros encontrados
        #esperamos por la aparicion del ultimo registro en base a su css
        last_row_id = "formMain:dataTable:%s:j_idt92" %(str(number_of_rows - 1))
        self.make_webdriver_wait(By.ID, last_row_id)
        return self.browser.page_source 

    def get_member_projects(self, member_id):
        url='http://sil2py.senado.gov.py/formulario/verProyectosParlamentario.pmf'\
          +'?q=verProyectosParlamentario%2F' + member_id
        self.browser.get(url)
        return self.browser.page_source

    def buscar_comisiones_por_periodo(self, period):
        #este item prrobablemente deberia ser todo un ciclo de navegacion
        # 1- del menu principal llamar al js de Comisiones por Período
        # 2- seleccionar camara (senadores o diputados)
        # 3- seleccionar periodo
        # 4- buscar (click en el boton)
        # 5- Parser: Extraer datos del resultado de (4)
        # 6- Invocar a [Integrantes]
        # 7- Parser: Extraer datos del resultado de (6)
        # 8- Cerrar pop up (7) y repetir desde 6 con el siguiente item
        self._call_menu_item(u'Comisiones por Período')
        self.make_webdriver_wait(By.ID, "formMain:idPeriodoParlamentario_input")
        select_camara_element = self.browser.find_element_by_id("formMain:idOrigen_input")
        select_camara = Select(select_camara_element)
        select_camara.select_by_index(1)#TODO: recibir el origen como parametro

        select_periodo_element = self.browser.find_element_by_id("formMain:idPeriodoParlamentario_input")
        select_periodo = Select(select_periodo_element)
        select_periodo.select_by_index(1)#TODO: recibir el periodo como parametro
        #se ejecuta la busqueda
        self.browser.execute_script("PrimeFaces.ab({source:'formMain:cmdBuscar',update:'formMain'});return false;")
        #esperar por el resultado
        rows_found = self.count_table_rows()
        waited_element = "formMain:dataTable:%s:j_idt101" % (rows_found)
        self.make_webdriver_wait(By.ID, waited_element)
        #parseo de resultado
        comisiones = self.parser.extraer_comisiones_por_periodo(self.browser.page_source)
        #invocar a integrantes_js_call
        for c in comisiones:
            self.browser.execute_script(c['integrantes_js_call'])
            time.sleep(2)
            miembros = self.parser.extraer_miembros_por_comision(self.browser.page_source)
            c['members'] = miembros
            
        return comisiones

    #period = 2014-2013
    #origin = D(diputados), S(senadores)
    def list_sessions_by_period(self, origin, period):
        self._call_menu_item(u'Sesiones por Período')
        self._make_driver_wait()
        self.make_webdriver_wait(By.ID, "formMain:idOrigen_input")
        select_camara_element = self.browser.find_element_by_id("formMain:idOrigen_input")
        select_camara = Select(select_camara_element)
        select_camara.select_by_value(origin)

        select_periodo_element = self.browser.find_element_by_id("formMain:idPeriodoParlamentario_input")
        select_periodo = Select(select_periodo_element)
        select_periodo.select_by_visible_text(period)
        self.browser.execute_script("PrimeFaces.ab({source:'formMain:cmdBuscar'" +\
                                    ",update:'formMain'});return false;")
        self._make_driver_wait()
        number_of_rows = self.count_table_rows()
        #we wait for the button in the lat row 
        #Ex: formMain:dataTable:53:toggle
        last_row_id = "formMain:dataTable:%s:toggle" %(str(number_of_rows - 1))
        self.make_webdriver_wait(By.ID, last_row_id)
        return self.browser.page_source 
    
    def download_attachment(self, origin, button_id, filename):
        #download attachments:
        # find button by id button_id': u'formMain:dataTableDetalle:3:j_idt113'
        # and click it
        button = self.browser.find_element_by_id(button_id)
        button.click()        
        session_id = self.browser.get_cookie('JSESSIONID')['value']
        viewstate = self.parser.extract_viewstate(self.browser.page_source)
        #TODO async?
        utils.download_file(origin, session_id, viewstate, filename)
        
    def obtener_detalle_de_proyecto(self, proyecto_id):
        #obtiene una comision e invoca a la url:
        #GET http://silpy.congreso.gov.py/formulario/VerDetalleTramitacion.pmf?q=VerDetalleTramitacion%2F + comision_id
        pass

    def buscar_proyectos_por_comision(self):
        # 1 - seleccionar del menu principal Proyectos por Comisión
        # 2 - seleccionar camara (Diputados o Senadores)
        # 3 - Click en boton de buscar.
        # 4 - almacenar lista para iterar por cada item
        # 5 - ir a VerProyectos y guardar referencia a 
        # 6 - extraer proyectos
        # 7 - empezar desde 1 utilizando la lista de (4)
        pass
            
    def list_projects_by_committee(self, js_call):
        #TODO:invoke js_call from data dictionary
        self.browser.execute_script(js_call)
        #count rows and wait for the last one
        number_of_rows = self.parser.number_of_rows_found(self.browser.page_source)
        last_row_id = 'formMain:dataTable:%s:acapite' %(number_of_rows - 1)    
        self.make_webdriver_wait(By.ID,last_row_id)
        return self.browser.page_source
            

#######################
### MainApp Section ###
#######################
from mongo_db import SilpyMongoClient
import urllib2

class SilpyScrapper(object):

    def __init__(self):   
        self.periods = ['2013-2014', '2014-2015']
        self.origins = ['D', 'S']
        self.navigator = SilpyNavigator()
        self.parser = SilpyHTMLParser()
        self.mongo_client = SilpyMongoClient()

    def close_navigator(self):
        self.navigator.close_driver()

    def get_members_data(self, origin):
        data = self.navigator.get_parlamentary_list(origin)
        rows = self.parser.parse_parlamentary_data(data)
        for row in rows:
            print 'procesando datos de: ' + row['name']
            member_id = row['id']
            url='http://sil2py.senado.gov.py/formulario/verProyectosParlamentario.pmf'\
                +'?q=verProyectosParlamentario%2F' + member_id
            response = urllib2.urlopen(url)
            html = response.read()
            args = {'id': row['id']
                    ,'projects': self.parser.parse_projects_by_parlamentary(html)}
            #download img
            filename = 'img/'+ row['id']+ '.jpg'
            urllib.urlretrieve(row['img'], filename)
        if origin=='S':
            print "Guardando datos de Senadores"
            self.mongo_client.update_senadores(rows)
        elif origin=='D':
            print "Guardando datos de Diputados"
            self.mongo_client.update_diputados(rows)

    def get_commiittees_by_period(self):
         periodo = '2014-2015'
         comisiones_periodo = self.navigator.buscar_comisiones_por_periodo()
         self.mongo_client.save_comisiones_por_periodo(periodo, comisiones_periodo)
        
    def get_sessions_by_period(self):
        #TODO
        #for period in self.periods:
        period = '2014-2015'
        origin='D'
        data = self.navigator.list_sessions_by_period(origin, period)
        session_list = self.parser.parsear_lista_sessiones(data)
        for s in session_list:
           #call and extract anexos: anexos_js_call
           #print s['index']+ ' - - '  +s['anexos_js_call']
           self.navigator.browser.execute_script(s['anexos_js_call'])
           #wait for the popup to load
           #formMain:dataTableDetalle:0:j_idt113 the id of the first button
           self.navigator.make_webdriver_wait(By.ID, "formMain:dataTableDetalle:0:j_idt113")
           #pass the resulting html to attachment extractor
           attachments = self.parser.extract_session_attachment(self.navigator.browser.page_source)
           #download attachments:
           # find button by button_id : u'formMain:dataTableDetalle:3:j_idt113'
           # and click it
           # for attachment in attachments:
           #     print attachment
           #     self.navigator.download_attachment(origin, 
           #                                        attachment['button_id'], 
           #                                        attachment['nombre'])
           #find and call button_id
           #call and extract proyectos

            
#############
##TEST CODE## 
#############
import threading
parser = SilpyHTMLParser()
senadores_scrapper = SilpyScrapper()
diputadossc_scrapper = SilpyScrapper()
senadores_scrapper.get_members_data('S')
diputadossc_scrapper.get_members_data('D')

# try:
#     thread.start_new_thread(senadores_scrapper.get_members_data('S'), ("Thread-1", 2, ) )
#     thread.start_new_thread( diputadossc_scrapper.get_members_data('D'), ("Thread-2", 4, ) )
# except:
#     print "Error: unable to start thread"

#sc.close_navigator()
# sc.get_commiittees_by_period()
# sc.get_sessions_by_period()
# html = utils.read_file_as_string('resources/leyes_parlamentario.html')
# soup = BeautifulSoup(html)
# print soup.find(id='formMain').find_all('div', {'role': 'tablist'})[0]['id']

# print parser.parse_projects_by_parlamentary(html)

