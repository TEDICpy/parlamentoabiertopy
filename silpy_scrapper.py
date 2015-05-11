#-*- coding: utf-8 -*-
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
import time

from request_content import committee_item_data

import hashlib 
import utils

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
        #TODO: set this as header
        description = soup.find(id="formMain:denominacion")       
        return self.parsear_lista_de_proyectos(result_tbody)

    def parsear_lista_de_proyectos(self, result_tbody):
        #result_body es tbody que contiene las filas de la tabla
        #Ej.: result_tbody = soup.find(id = "formMain:dataTableProyecto_data") 
        #extracts data from the results table in resources/projects_by_committee.html
        tr_list = result_tbody.find_all("tr", recursive=False)
        projects = []
        
        for tr in tr_list:
            td_list = tr.find_all("td", recursive=False)            
            if td_list != None and len(td_list) > 0:
                project = {}
                td0 = td_list[0]

                if td0.div != None:
                    project['titulo'] = td0.a.text                   
                span_list = td0.find_all('span')
                if span_list != None and len(span_list) > 0:
                    project['tipo'] = span_list[0].text.strip()
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
                        project['ingreso'] = date.strip()
                        project['expediente'] = id.strip()
                        
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
                                    project['mensajes'] = messages

                #segunda columna: Etapa
                if len(td_list) >= 1:
                    td1 = td_list[1]
                    td1_span_list = td1.find_all('span')
                    #print "td1_span_list " + str(td1_span_list)
                    if len(td1_span_list) > 1:
                        project['etapa'] = {'camara': td1_span_list[0].text, td1_span_list[1].text : td1_span_list[2].text} 

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
        proyecto = {}
        soup = BeautifulSoup(html)
        periodo = soup.find(id = 'formMain:idPeriodoParlamentario_label')
        periodo = periodo.text.strip()
        tbody = soup.find(id = 'formMain:dataTable_data')
        tr_list = tbody.find_all('tr')
        for tr in tr_list:
            td_list = tr.find_all('td')
            if len(td_list) > 0:
                proyecto['index'] = td_list[0].text.strip()
                proyecto['fecha'] = td_list[1].div.text.strip()
                proyecto['nro_sesion'] = td_list[2].text.strip()
                proyecto['tipo_sesion'] = td_list[3].text.strip()
                proyecto['anexos_js_call'] = td_list[4].button['onclick']
                proyecto['verProyectos_js_call'] = td_list[5].button['onclick']
                proyectos.append(proyecto)

        return proyectos

    def extraer_comisiones_por_periodo(self, html):
        soup = BeautifulSoup(html)
        tbody = soup.find(id='formMain:dataTable_data')
        tr_list = tbody.find_all('tr', recursive=False)
        comisiones = []

        for tr in tr_list:
            comision = {}
            td_list = tr.find_all('td', recursive=False)
            comision['denominacion'] = td_list[1].text.strip()
            comision['tipo']  = td_list[2].text.strip()
            comision['camara'] = td_list[3].text.strip()
            comision['integrantes_js_call'] = td_list[4].div.button['onclick']
            comisiones.append(comision)
        return comisiones

    def extraccion_de_informacion_de_proyecto(self, html):
        soup = BeautifulSoup(html)
        info_div = soup.find(id='formMain:j_idt81_content')
        
        #informacion del proyecto
        info = {}
        info['expediente'] = info_div.find(id='formMain:expedienteCamara').text.strip()
        info['tipo'] = info_div.find(id='formMain:idTipoProyecto').text.strip()
        info['materia'] = info_div.find(id='formMain:idMateria').text.strip()
        info['urgencia'] = info_div.find(id='formMain:idUrgencia').text.strip()
        info['fecha_ingreso'] = info_div.find(id='formMain:fechaIngreso').text.strip()
        info['iniciativa'] = info_div.find(id='formMain:idTipoIniciativa').text.strip()
        info['origen'] = info_div.find(id='formMain:idOrigen').text.strip()
        info['mensaje_pe'] =info_div.find(id='formMain:numeroMensaje').text.strip()
        info['acapite'] =info_div.find(id='formMain:acapite').text.strip()

        #'Etapa de la Tramitación'
        etapa = {}
        etapas_table = soup.find(id='formMain:panelEtapas')
        etapa['etapa'] = etapas_table.find(id='formMain:idEtapaProy').text.strip()
        etapa['sub_etapa'] = etapas_table.find(id='formMain:idSubEtapaProy').text.strip()
        etapa['estado'] = etapas_table.find(id='formMain:idEstadoProyecto').text.strip()

        #detalle de tramitacion
        tbody_content = soup.find(id='formMain:dataTableTramitacion_data')
        tr_list = tbody_content.find_all('tr', recursive=False)

        tramitaciones = []
        for tr in tr_list:
            tramitacion = {}
            td_list = tr.find_all('td')

            tramitacion['index'] = td_list[0].text.strip()
            tramitacion['sesion'] = td_list[1].text.strip()
            tramitacion['fecha'] = td_list[2].text.strip()

            #TODO: extraccion de etapa se puede generalizar
            if len(td_list) >= 1:
                td1 = td_list[3]
                td1_span_list = td1.find_all('span')
                #print "td1_span_list " + str(td1_span_list)
                if len(td1_span_list) > 1:
                    tramitacion['etapa'] = {'camara': td1_span_list[0].text, td1_span_list[1].text : td1_span_list[2].text} 

            #Resultado
            #TODO: todo esto es un kilombo, aqui hay de todo
            tramitacion['resultado'] = td_list[4]
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
            p['nombre'] = td_list[1].text.strip()
            p['camara'] = td_list[2].text.strip()
            p['cargo'] = td_list[3].text.strip()
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


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

class SilpyNavigator(object):
    """
    Naviagation Flow for 
    """

    def __init__(self):
        self.parser = SilpyHTMLParser()
        self.browser = utils.get_new_browser()
        self.browser.get("http://silpy.congreso.gov.py/main.pmf")
                               
    def make_webdriver_wait(self, by, waited_element):
        try:
            wait = WebDriverWait(self.browser, 15)
            wait.until(EC.presence_of_element_located((by, waited_element)))
            print "Page is ready! Loaded: " + waited_element
        
        except TimeoutException:
            print "Loading took too much time!"

    def count_table_rows(self):
        #wait for css_element
        #TODO: css element as parameter
        css_element = ".ui-widget-content.ui-datatable-even"
        self.make_webdriver_wait(By.CSS_SELECTOR, css_element)
        return self.parser.number_of_rows_found(self.browser.page_source)
        
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
        #WARNING: this is a bug
        # the css class .ui-widget-content.ui-datatable-even can be even or odd depending on the number of rows
        #use 'data-ri' instead of css ?
        self.make_webdriver_wait(By.CSS_SELECTOR, '.ui-widget-content.ui-datatable-even')#".ui-datatable-header.ui-widget-header")
        number_of_rows = self.parser.number_of_rows_found(self.browser.page_source) #extraemos la cantidad de registros encontrados
        #esperamos por la ultima aparicion del registro en base a su css
        last_row_id = "formMain:dataTable:%s:j_idt92" %(str(number_of_rows - 1))
        self.make_webdriver_wait(By.ID, last_row_id)
        return self.browser.page_source 

    def buscar_comisiones_por_periodo(self):
        #este item prrobablemente deberia ser todo un ciclo de navegacion
        # 1- del menu principal llamar al js de Comisiones por Período
        # 2- seleccionar camara (senadores o diputados)
        # 3- seleccionar periodo
        # 4- buscar (click en el boton)
        # 5- Parser: Extraer datos del resultado de (4)
        # 6- Invocar a [Integrantes]
        # 7- Parser: Extraer datos del resultado de (6)
        # 8- Cerrar pop up (7) y repetir desde 6 con el siguiente item
        html = self.browser.page_source
        
        menu = self.parser.extraer_items_menu(html)
        for key, val in menu.items():
            if key == u'Comisiones por Período':
                js_call = val
                break
        if js_call:
            self.browser.execute_script(js_call)

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
            c['miembros'] = miembros
            
        return comisiones

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

class SilpyScrapper(object):

    def __init__(self):   
        self.navigator = SilpyNavigator()
        self.parser = SilpyHTMLParser()
        self.mongo_client = SilpyMongoClient()

    def get_parlamentary_list(self):
        data = self.navigator.get_parlamentary_list('S')
        rows = self.parser._extract_parlamentary_data(data)
        self.mongo_client.save_senadores(rows)
        
    def get_commiittees_by_period(self):
         periodo = '2014-2015'
         comisiones_periodo = self.navigator.buscar_comisiones_por_periodo()
         self.mongo_client.save_comisiones_por_periodo(periodo, comisiones_periodo)
        


#############
##TEST CODE## 
#############

sc = SilpyScrapper()
sc.get_parlamentary_list()
sc.get_commiittees_by_period()
# update_data = 'resources/buscar_parlamentarios_update.html'
#lista_parlamentarios = 'resources/lista_parlamentarios.html'
# projects_by_committee = 'resources/projects_by_committee.html'

# filename = 'resources/informacion_proyecto.html'

# from utils import *
# html = read_file_as_string(filename)

# tramitaciones = parser.extraccion_de_informacion_de_proyecto(html)
# for t in tramitaciones:
#     print t['etapa']
