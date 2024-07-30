
import pandas as pd
import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep, time
from random import choice

start_time = time()

pd.options.mode.chained_assignment = None  # default='warn'

#def pre_filtro(file):

file = f'{os.getcwd()}\Lista_imoveis\Lista_imoveis_SP.csv'

df = pd.read_csv(file, sep = ';', encoding="ISO-8859-1", header=1)

#Filtrar para apenas Leilao SFI - Edital Unico
df = df.where(df['Modalidade de venda'] == 'Leilão SFI - Edital Único').dropna()

#df.to_csv('teste_imoveis.csv', encoding="ISO-8859-1")

#### EXTRAINDO INFORMAÇÕES DA DESCRIÇÃO


#Extraindo 'Tipo de Lugar'
df['Tipo de Lugar'] = df.apply(lambda x:re.findall("^(.*?),", x['Descrição'])[0], axis=1)

#Extraindo 'Area Total'
df['Area Total'] = df.apply(lambda x: re.findall("\d.*(?= de área total)", x['Descrição'])[0], axis=1)

#Extraindo 'Area Privativa'
df['Area Privativa'] = df.apply(lambda x: re.findall("\d+.\d+(?= de área privativa)", x['Descrição'])[0], axis=1)

#Extraindo 'Area do Terreno'
df['Area do Terreno'] = df.apply(lambda x: re.findall("\d+.\d+(?= de área do terreno)", x['Descrição'])[0], axis=1)

#Extraindo 'Quartos'
df['Quartos'] = df.apply(lambda x: re.findall("\d+(?= qto)", x['Descrição']), axis=1)
df['Quartos'] = df['Quartos'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha quarto (preenche com 0)

#Extraindo 'Garagem'
df['Garagem'] = df.apply(lambda x: re.findall("\d+(?= vaga\(s\))", x['Descrição']), axis=1)
df['Garagem'] = df['Garagem'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha garagem (preenche com 0)

#Extraindo 'Sala'
df['Sala'] = df.apply(lambda x: re.findall("\d+(?= sala\(s\))", x['Descrição']), axis=1)
df['Sala'] = df['Sala'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha sala (preenche com 0)

### Acessando o Link para 'Descrição Extra'

#Extraindo 'Financiamento' da Descrição Extra
sleep_time = [0.8, 0.7, 2, 1.3, 1.5, 1.7, 3.5, 3.1, 3.2]
df_teste = df.head(100)


chrome_options = Options()
#chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--start-maximized")

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

for index, url in df_teste['Link de acesso'].items():

    driver.get(url=url)
    driver.implicitly_wait(2)

    sleep(choice(sleep_time)) #choose random sleep time

    #elements = driver.find_elements(By.CLASS_NAME, 'related-box')
    elements = driver.find_elements(By.XPATH, '/html/body/div[1]/form/div[1]/div/div[3]/p[3]')

    descr_extra = ''

    for i in elements:
        descr_extra += i.text

    df_teste.loc[index, 'Descrição Extra'] = descr_extra

df_teste.to_csv('teste_imoveis.csv', encoding="ISO-8859-1")

delta = time() - start_time 

print(f"Tempo de execução: {delta:.2f} segundos")

driver.quit()










"""
url = 'https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel=8787712038403'
proxies = {
   'http': 'http://152.26.229.86:9443',
   'https': 'http://89.219.10.34:8085'
}
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

r = requests.get(url, proxies=proxies, headers=headers)  # , verify=False

print(r.text)
"""