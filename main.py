
#from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import pandas as pd
from pre_filtro import *

#Exclui o arquivo antigo 'Lista_imoveis_SP'
os.remove(f'{os.getcwd()}\Lista_imoveis\Lista_imoveis_SP.csv')

#Configurandoa as opçoes do navegador: 'headless'
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
#chrome_options.add_argument("--allow-insecure-localhost")
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument("--headless=new")

#Muda a pasta de download para 'Lista_imoveis' (relativo)
prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": 
                        f'{os.getcwd()}\Lista_imoveis',#IMPORTANT - ENDING SLASH V IMPORTANT
             "directory_upgrade": True}
chrome_options.add_experimental_option("prefs", prefs)
service = Service("chromedriver.exe")


#Iniciando driver e fazendo a request
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp")
driver.implicitly_wait(2)

#Selecionar o Estado SP
select_element = driver.find_element(By.NAME, 'cmb_estado')
select = Select(select_element)
select.select_by_value('SP')

#Clicar no Botao 'Proximo' para baixar o arquivo
button = driver.find_element(By.ID, "btn_next1").click()

#Esperar até finalizar o download
time.sleep(2)

#Fecha o driver
driver.quit()

pre_filtro(f'{os.getcwd()}\Lista_imoveis\Lista_imoveis_SP.csv')


