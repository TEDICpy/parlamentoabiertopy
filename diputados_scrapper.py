#-*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

import utils

#In this file we process data comming from
#http://www.diputados.gov.py
#TODO:

class DiputadosScrapper(object):
    
    #en el sitio de diputados se hace un
    #request por cada tab del detalle del diputado:
    # Datos Currículum Comisiones Proyectos» Contactos 
    
    def get_member_list(self):
        url = 'http://www.diputados.gov.py/ww2/?pagina=dip-listado'
        #response = requests.get(url)
        html = utils.read_file_as_string('resources/diputados/lista.html')
        soup = BeautifulSoup(html)#(response.text)
        table = soup.find('table', {'class':'tex'})
        tr_list = table.tbody.find_all('tr', recursive=False)
        tr_list.pop(0)#discard first row, header
        members = []
        for tr in tr_list:
            member = {}
            td_list = tr.find_all('td', recursive=False)
            id = td_list[0].img['src']
            member['id'] = id[id.index('/')+2:id.index('.')]#
            member['img_src'] = td_list[0].img['src']#so we can download image afterwards
            member['name'] = td_list[1].text.strip()
            member['link'] = td_list[1].a['href']
            members.append(member)
        return members
    
    def get_member_detail(self, member):
        #url = 'http://www.diputados.gov.py/ww2/index.php?pagina=cv&id=271'
        html = utils.read_file_as_string('resources/diputados/detalle_diputado.html')
        soup = BeautifulSoup(html)
        tables = soup.find_all('table', {'class':'tex'})#the child table is the one we need
        tbody = tables[1].find_all('tbody')[1]#and of course also the seccond tbody
        member = {}
        td_list = tbody.find_all('td')
        member['departament'] = td_list[1].text.strip()
        member['city'] = td_list[3].text.strip()
        member['party'] = td_list[5].text.strip()
        member['bench'] = td_list[7].text.strip()
        member['profession'] = td_list[9].text.strip()
        member['office'] = td_list[11].text.strip()
        member['phone'] = td_list[13].text.strip()
        member['web_site'] = td_list[15].text.strip()
        member['email'] = td_list[17].text.strip()                
        return member
        
    def get_member_cv(self, member_id):
        #http://www.diputados.gov.py/ww2/index.php?pagina=cv-curriculum&id=271
        html = utils.read_file_as_string('resources/diputados/detalle_diputado_cv.html')
        soup = BeautifulSoup(html)
        table = soup.find('table', {'class':'tex'})
        tables = soup.find_all('table', {'class':'tex'})#the child table is the one we need
        tbody = tables[1].tbody
        #return raw, not much to do with this right now as all cv data is structured differentyl
        return str(tbody)
    
    def get_member_committees(self, member):
        #http://www.diputados.gov.py/ww2/index.php?pagina=cv-comisiones&id=271    
        html = utils.read_file_as_string('resources/diputados/detalle_diputado_comisiones.html')
        soup = BeautifulSoup(html)
        table = soup.find('table', {'class':'tex'})
        tables = soup.find_all('table', {'class':'tex'})#the child table is the one we need
        tbody = tables[1].tbody
        print tbody

    def get_articles(self):
        day = '21'
        month = '05'
        year = '2015'
        requests.post('http://www.diputados.gov.py/ww2/index.php?pagina=noticias-lista',
                      files={'dia': (None, day), 'mes': (None, month), 
                             'anho': (None, year), 'sb': (None, '1'), 
                             'btnBuscar': (None, 'Buscar')})


ds = DiputadosScrapper()
#members = ds.get_member_list()
ds.get_member_committees('id')
