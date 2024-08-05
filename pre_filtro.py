
import pandas as pd
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep, time
from random import choice
from progress.bar import IncrementalBar
from geopy.geocoders import Nominatim
from geopy import distance

pd.options.mode.chained_assignment = None  # default='warn'

start_time = time()

# INICIO:: FUNÇÕES DE EXTRAÇÃO E INICIALIZAR

def check_error(driver):

    error_title1 = 'Ocorreu um erro ao tentar recuperar os dados do imóvel.\nO imóvel que você procura não está mais disponível para venda.'
    error_title2 = 'O imóvel que você procura não está mais disponível para venda.'

    #Check if the page shows the error title
    check_error = driver.find_element(By.XPATH, '/html/body/div[1]/form/div/div/div/h5').text
    
    if (check_error == error_title1) or (check_error == error_title2):
        return True
    else:
        return False


def extrair_descricao(dataframe):

    #Extraindo 'Tipo de Lugar'
    dataframe['Tipo de Lugar'] = dataframe.apply(lambda x:re.findall("^(.*?),", x['Descrição'])[0], axis=1)

    #Extraindo 'Area Total'
    dataframe['Area Total'] = dataframe.apply(lambda x: re.findall("\d.*(?= de área total)", x['Descrição'])[0], axis=1)

    #Extraindo 'Area Privativa'
    dataframe['Area Privativa'] = dataframe.apply(lambda x: re.findall("\d+.\d+(?= de área privativa)", x['Descrição'])[0], axis=1)

    #Extraindo 'Area do Terreno'
    dataframe['Area do Terreno'] = dataframe.apply(lambda x: re.findall("\d+.\d+(?= de área do terreno)", x['Descrição'])[0], axis=1)

    #Extraindo 'Quartos'
    dataframe['Quartos'] = dataframe.apply(lambda x: re.findall("\d+(?= qto)", x['Descrição']), axis=1)
    dataframe['Quartos'] = dataframe['Quartos'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha quarto (preenche com 0)

    #Extraindo 'Garagem'
    dataframe['Garagem'] = dataframe.apply(lambda x: re.findall("\d+(?= vaga\(s\))", x['Descrição']), axis=1)
    dataframe['Garagem'] = dataframe['Garagem'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha garagem (preenche com 0)

    #Extraindo 'Sala'
    dataframe['Sala'] = dataframe.apply(lambda x: re.findall("\d+(?= sala\(s\))", x['Descrição']), axis=1)
    dataframe['Sala'] = dataframe['Sala'].apply(lambda x: x[0] if len(x) >= 1 else 0) # caso não tenha sala (preenche com 0)

    return dataframe
def escrever_descricaoExtra(df, num_linhas_inicio=0, num_linhas_final=5):
    #Como ainda esta em versao teste, usamos apenas o head(num_linhas) que vao ser adquiridas as informações
    # retorna 0 se funcionou e escreve um arquivo 'teste_imoveis.csv' como resultado da operação
    
    sleep_time = [0.8, 0.7, 2, 1.3, 1.5, 1.7, 2.5, 3.1, 3.2]
    df_teste = df[num_linhas_inicio:num_linhas_final+1]

    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=1")

    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    num_linhas_procesasdas = df_teste.shape[0]
    bar = IncrementalBar("Processando...", max=num_linhas_procesasdas) #Definindo a barra de carregamento

    for index, url in df_teste['Link de acesso'].items():

        driver.get(url=url)
        driver.implicitly_wait(2)

        sleep(choice(sleep_time)) #choose random sleep time

        #First Check if the site housing exists
        if check_error(driver=driver): #True for Error
            #Delete the Row
            df_teste = df_teste.drop(index)

        else:
            elements_extra = driver.find_elements(By.XPATH, '/html/body/div[1]/form/div[1]/div/div[3]/p[3]')
            data2Leilao = driver.find_elements(By.XPATH, '/html/body/div[1]/form/div[1]/div/div[3]/span[5]')
            valor2Leilao = driver.find_elements(By.XPATH, '/html/body/div[1]/form/div[1]/div/div[2]/p')

            descr_extra = ''

            for i in elements_extra:
                descr_extra += i.text

            df_teste.loc[index, 'Descrição Extra'] = descr_extra
            df_teste.loc[index, 'Data 2º Leilão'] = data2Leilao[0].text[20:] #slice '<data> - <horario>'
            df_teste.loc[index, 'Valor de venda 2º Leilão'] = re.search("(2º Leilão: R\$ )([\d.,]+)", valor2Leilao[0].text).group(2)
        
        bar.next()

    #df_teste.to_csv('teste_imoveis.csv', encoding="ISO-8859-1")
    bar.finish()

    delta = time() - start_time 
    print(f"Tempo de execução: {delta:.2f} segundos")

    driver.quit()
    return df_teste
def calculo_distancia(df, referencia, sigla_estado):

    # usando a lib 'geopy' e um algoritmo especifico para que não seja necessário recalcular a mesma distância
    # mais de uma vez (gravando as dist. em um dicionário)

    geolocator = Nominatim(user_agent="InsaneDistanceCalculatorAwShit")

    c1 = referencia
    loc1 = ((geolocator.geocode(c1).latitude, geolocator.geocode(c1).longitude))


    dict_distancia = {referencia+" "+sigla_estado: 0}


    for index, cidade in df['Cidade'].items():
        cidade = f'{cidade.strip()} {sigla_estado}'

        if dict_distancia.get(cidade) is None:
            loc2 = ((geolocator.geocode(cidade).latitude, geolocator.geocode(cidade).longitude))
            result = round(float(distance.distance(loc1, loc2).km)*1.1, 2) #Adicionando 12% e deixando com 2 casas decimais
            dict_distancia[cidade] = result

        else:
            result = dict_distancia[cidade]

        df.loc[index, 'Distância [km]'] = result

    return df
    
# FIM:: FUNÇÕES DE EXTRAÇÃO E INICIALIZAR


file = f'{os.getcwd()}\Lista_imoveis\Lista_imoveis_SP.csv'
df = pd.read_csv(file, sep = ';', encoding="ISO-8859-1", header=1)

#Filtrar para apenas Leilao SFI - Edital Unico
df = df.where(df['Modalidade de venda'] == 'Leilão SFI - Edital Único').dropna()


df = extrair_descricao(df)
df = escrever_descricaoExtra(df, num_linhas_inicio=228, num_linhas_final=300)

#Inserindo a coluna 'Financiamento'
df['Financiamento'] = df.apply(lambda x: 0 if len(re.findall("\S* \w* (?=financiamento)", x['Descrição Extra'])) != 0 else 1, axis=1)

# Inserindo a coluna 'Distancia'
df = calculo_distancia(df=df, referencia='SANTO ANDRÉ', sigla_estado='SP')

#Salvando o arquivo
df.to_csv('teste_imoveis.csv', encoding="ISO-8859-1")
