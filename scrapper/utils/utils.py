#-*- coding: utf-8 -*-
import os
from subprocess import call
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By


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
      +' -H "Content-Length: 248"'\
      +' --data '+ data\
      +' --compressed'\
      +' -o ' + filename
    
    print command_diputados
    os.system(command_diputados)

    # data = '"formMain=formMain&formMain%3AidOrigen_input=S'\
    #   +'&formMain%3AidPeriodoParlamentario_input=100043'\
    #   +'&formMain%3AdataTableDetalle%3A0%3Aj_idt113='\
    #   +'&formMain%3AdataTableProyecto_scrollState=0%2C0&javax.faces.ViewState='\
    #   +viewstate + '"'
    # var = ['-H', cookie, '--data', data, '--compressed']
    # command = attachments_command + var
    # command = ["curl", "http://sil2py.senado.gov.py/formulario/ListarSesion.pmf", 
    #                        '-H', '"Host: sil2py.senado.gov.py"',
    #                        '-H', '"User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0"',
    #                        '-H', '"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"',
    #                        '-H', '"Accept-Language: en-US,en;q=0.5"', 
    #                        '-H', '"Accept-Encoding: gzip, deflate"',
    #                        '-H', '"Referer: http://sil2py.senado.gov.py/formulario/ListarSesion.pmf"',
    #                        '-H', '"Connection: keep-alive"', 
    #                        '-H', '"Content-Type: application/x-www-form-urlencoded"', 
    #                        '-H', '"Content-Length: 248"',
    #                        '-H', cookie, 
    #                        '-H', '"Connection: keep-alive"',
    #                        '-H', '"Pragma: no-cache"',
    #                        '-H', '"Cache-Control: no-cache"',
    #                        '--data', data, '--compressed',
    #            '-o', 'file.pdf']
