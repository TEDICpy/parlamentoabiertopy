#-*- coding: utf-8 -*-
import os
import sys
import hashlib
from subprocess import call
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

import requests
import time
BROWSER_WAIT=60

attachments_command = ["curl", "http://sil2py.senado.gov.py/formulario/ListarSesion.pmf", 
'-H', '"Host: sil2py.senado.gov.py"',
'-H', ' "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"',
'-H', ' "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
'-H', ' "Accept-Language: en-US,en;q=0.5" -H "Accept-Encoding: gzip, deflate"',
'-H', ' "Referer: http://sil2py.senado.gov.py/formulario/ListarSesion.pmf"',
'-H', ' "Connection: keep-alive" -H "Content-Type: application/x-www-form-urlencoded"', 
'-H', ' "Content-Length: 248"']

def get_new_browser():
#     browser = webdriver.Firefox()
     browser = webdriver.PhantomJS()
     browser.set_window_size(1120, 550)
     return browser

def _wait_document_ready_callback(browser):
    is_complete = browser.execute_script("return document.readyState;")
    if (is_complete == "complete"):
        return True

def wait_for_document_ready(browser):
     try:
          wait = WebDriverWait(browser, BROWSER_WAIT)
          wait.until(_wait_document_ready_callback, browser)
     except TimeoutException:
          print "Loading took too much time!"

def make_webdriver_wait(by, waited_element, browser):
     try:
          wait = WebDriverWait(browser, BROWSER_WAIT)
          wait.until(EC.presence_of_element_located((by, waited_element)))
          print "Page is ready! Loaded: " + waited_element
        
     except TimeoutException:
          print "Loading took too much time! for element: " + waited_element

def read_file_as_string(file):
    f = ''
    htmlfile = open(file)
    for l in htmlfile:
        f +=l
    return f

def curl_command(session_id, url, data, filename, dir):
     if not os.path.exists(dir):
          os.makedirs(dir)

     if dir[::-1].index('/'):
          dir += '/' 
     #give a generic name
     #read the actualname from the .header file
     #rename the fiel to the name in the header file
     rename = False
     if filename == None:
          filename = hashlib.sha1(session_id+url+data+ dir).hexdigest()
          rename = True
          
     out = dir+filename
     command = u'curl ' + url \
          +' -H "Host: sil2py.senado.gov.py"'\
          +' -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'\
          +' -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'\
          +' -H "Accept-Language: en-US,en;q=0.5"'\
          +' -H "Accept-Encoding: gzip, deflate"'\
          +' -H "Cookie: primefaces.download=true; JSESSIONID='+ session_id + '"'\
          +' -H "Connection: keep-alive"'\
          +' -H "Content-Type: application/x-www-form-urlencoded"'\
          +' --data "'+ data + '"'\
          +' --compressed'\
          +' -o ' + out \
          +' --dump-header ' + out+'.header'\

     command = command.encode('utf-8')
     os.system(command)
     f = open(out+'.header')
     lines = f.readlines()
     r = [x for x in lines if 'filename' in x]#name extracted from header
     #si no encuentra el nombre aqui es porque no bajo nada :/
     if rename and len(r) > 0:
          r = r[0]
          new_filename = r[r.index('filename')+len('filename='):r.index('\r')] \
          .replace('"','').encode('utf-8')
          print "renamig file to %s" %(new_filename)
          os.rename(out, dir+new_filename)
          return dir+new_filename
     elif len(r) == 0:
          print "this failed"
          print "filename %s" %(filename)
          print "retrying..."
          time.sleep(2)
          print command
          os.system(command)
          
     return dir+filename

def download_bill_directive(row_index, button_index, project_id, viewstate, session_id):
     #use the whole button id after the &?
     #dictamenes
     url = "http://sil2py.senado.gov.py/formulario/VerDetalleTramitacion.pmf"
     if button_index == None:
          button_index = "0"
     data = "formMain=formMain&formMain%3Aj_idt124%3Aj_idt203%3A" + str(row_index) + \
            "%3Aj_idt211%3A0%3Aj_idt214%3A" + str(button_index) + \
            "%3Aj_idt216=&formMain%3Aj_idt124_activeIndex=3&javax.faces.ViewState=" + viewstate
     dirname = 'download/bills/%s/directives' %(project_id)
     return curl_command(session_id, url, data, None, dirname)

def download_bill_resolutions_and_messages(row_index, button_index, filename, project_id, viewstate, session_id):
     if button_index == None:
          button_index = "0"
     url = "http://sil2py.senado.gov.py/formulario/VerDetalleTramitacion.pmf"
     # data = "formMain=formMain&formMain%3Aj_idt124%3Aj_idt220%3A" + str(row_index) + \
     #        "%3Aj_idt233%3A" + str(button_index) + \
     #        "%3Aj_idt234=&formMain%3Aj_idt124_activeIndex=4&javax.faces.ViewState=" +\
     #        viewstate

     data = "formMain=formMain&formMain%3Aj_idt124%3Aj_idt220%3A" + str(row_index) \
            + "%3Aj_idt233%3A" + str(button_index) \
            + "%3Aj_idt234=&formMain%3Aj_idt124_activeIndex=4&javax.faces.ViewState=" \
            + viewstate
     dirname = 'download/bills/%s/resolutions_and_messages' %(project_id)
     return curl_command(session_id, url, data, filename, dirname)
    
def download_bill_document(index, filename, project_id, viewstate, session_id):
     dirname = 'download/bills/%s/documents' %(project_id)
     url = "http://sil2py.senado.gov.py/formulario/VerDetalleTramitacion.pmf"
     viewstate = viewstate.replace(':','%3A') 
     data = 'formMain=formMain&formMain%3Aj_idt124%3AdataTableDetalle%3A' + str(index) \
            + '%3Aj_idt186=&formMain%3Aj_idt124_activeIndex=1&javax.faces.ViewState=' + viewstate
     return curl_command(session_id, url, data, filename, dirname)

def download_file(origin, session_id, viewstate, filename):
#TODO: pass period id (100063) and origin ('S' or 'D')
#-H "Cookie: primefaces.download=true; JSESSIONID=21510a5ea2ed66961d5e3b5dd4ba", 
#'--data "formMain=formMain&formMain%3AidOrigen_input=D&formMain%3AidPeriodoParlamentario_input=100063&formMain%3AdataTableDetalle%3A0%3Aj_idt113=&formMain%3AdataTableProyecto_scrollState=0%2C0&javax.faces.ViewState=-5058637369442208233%3A1553529024225037061"',
    #call(['curl',])
    print viewstate
    filename = filename.encode('ascii', 'ignore') #.replace('Á', 'A').replace('Ó', '0')
    cookie = '"Cookie: primefaces.download=true; JSESSIONID=%s"' %(session_id)
    viewstate = viewstate.replace(':','%3A') 
    data = '"formMain=formMain&formMain%3AidOrigen_input=' + origin + '&formMain%3AidPeriodoParlamentario_input=100063&formMain%3AdataTableDetalle%3A0%3Aj_idt113=&formMain%3AdataTableProyecto_scrollState=0%2C0&javax.faces.ViewState='+viewstate + '"'
    command_diputados = 'curl "http://sil2py.senado.gov.py/formulario/ListarSesion.pmf"'\
      +' -H "Host: sil2py.senado.gov.py"'\
      +' -H "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"'\
      +' -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'\
      +' -H "Accept-Language: en-US,en;q=0.5"'\
      +' -H "Accept-Encoding: gzip, deflate"'\
      +' -H "Referer: http://sil2py.senado.gov.py/formulario/ListarSesion.pmf"'\
      +' -H "Cookie: primefaces.download=true; JSESSIONID='+ session_id + '"'\
      +' -H "Connection: keep-alive"'\
      +' -H "Content-Type: application/x-www-form-urlencoded"'\
      +' --data '+ data\
      +' --compressed'\
      +' -o ' + filename
    
    print command_diputados
    os.system(command_diputados)
