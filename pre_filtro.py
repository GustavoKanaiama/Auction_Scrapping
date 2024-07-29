
import pandas as pd
import os

#def pre_filtro(file):

file = f'{os.getcwd()}\Lista_imoveis\Lista_imoveis_SP.csv'

df = pd.read_csv(file, sep = ';', encoding="ISO-8859-1", header=1)

#Filtrar para apenas Leilao SFI - Edital Unico
df = df.where(df['Modalidade de venda'] == 'Leilão SFI - Edital Único').dropna()

print(df)

df.to_csv('teste_imoveis.csv', encoding="ISO-8859-1")