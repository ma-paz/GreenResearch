import pandas as pd
import numpy as np
from collections import Counter
import openai
from openai import OpenAI

# Función para leer un archivo de texto y convertirlo en una lista
def leer_archivo_a_lista(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        lista = archivo.read().splitlines()
    return lista

#Función para quitar los clones de un pandas array
def quitar_duplicados(datos):
    '''
    Quita todo los elementos duplicados de un dataframe en pandas\n
    datos=dataframe
    '''
    # Convertir los diccionarios a cadenas JSON para que sean hashables
    for col in datos.columns:
        if datos[col].apply(lambda x: isinstance(x, dict)).any():
            datos[col] = datos[col].apply(lambda x: str(x) if isinstance(x, dict) else x)
    
    return datos.drop_duplicates()

#Función que recolecta una lista con todas las palabras que encontramos en una columna
def palabras_columna(dataframe, abstracto_o_titulo):
    '''
    Función que recolecta una lista con todas las palabras únicas que encontramos en una columna\n
    abstracto_o_titulo:\n
    1=abstracto
    *=titulo
    '''
    # Tokenización y recuento de palabras en todas las descripciones
    if abstracto_o_titulo != 1:
        palabras = ' '.join(dataframe['Title']).replace("(","").replace("e.g","").replace(")","").replace(",","").replace(".","").split()
    else:
        palabras = ' '.join(dataframe['Abstract']).replace("(","").replace(")","").replace(",","").replace(".","").split()

    # Pasando palabras a lowercase para fitrar de manera más eficiente
    palabras= [palabra.lower() for palabra in palabras]

    # Lista de palabras de conexión o relleno a excluir
    skip = leer_archivo_a_lista('extra_words.txt')

    # Filtrar palabras únicas excluyendo las de relleno
    palabras_unicas = set([palabra for palabra in set(palabras) if palabra not in skip])

    return list(palabras_unicas)


#Función que conecta a las palabras del filtro 
def Seleccionar_outliers_small(lista_completa, original_prompt, contexto, tokens=100, model="gpt-3.5-turbo"):
    
    #Escribir función que ayuda a seleccionar outliers, considerar la necesidad de incorporar la voluntad del usuario, posible ayuda de ia
    client = OpenAI()
    who= 'You are a helptful assistant for data analysis.'#lo hago así para leerlo bien en caso de editarlo en el futuro
    I1='I want you to create a list of words that have nothing to do with a particular topic or theme.\n' 
    I2='\n Here is the original topic \n' 
    I3='\n And this is the list of words: \n'
    I4='\n Now, this is a bit of context to help you find these words that have nothing to do with the topic or the context: '
    I5='Finally, is an example of the format i want for the answer (use this format and nothing else)(i want the words divided by a coma): Cities, Iot, Cloud, Hardware\n\n'
    prompt=I1 + I2 + original_prompt+ I3+ ','.join(lista_completa)+ I4 + contexto + I5
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": who},
                {"role": "user", "content": prompt}
            ],
            max_tokens=tokens,
            temperature=0.7,
        )
        resultado=(response.choices[0].message.content).split(',')
        return resultado
    except Exception as e:
        return f"Error: {e}"
        
#okay vamos a llamar varias veces a esta prompt desde zero
def Seleccionar_outliers(lista_completa, original_prompt, contexto, tokens=100):
    results=''
    i=0
    while i<=len(lista_completa):
        if i+100<len(lista_completa):
            chunk=lista_completa[i:i+100]
        else:
            chunk=lista_completa[i:]        
        i+=100
        results+=(Seleccionar_outliers_small(chunk,original_prompt,contexto))
    return results

#Función que saca elementos repetidos de una columna por outliers
def Filtrar_outliers(documento, lista_outliers, abstracto_o_titulo):
    '''
    abstracto_o_titulo:\n
    1=abstracto\n
    *=titulo
    '''
    if abstracto_o_titulo!=1:
        columna = 'Title'
    else:
        columna = 'Abstract'

    return documento[~documento[columna].str.contains('|'.join(lista_outliers), case=False)]

#Función para procesamiento rapido de abstractos con AI
def quick_reading_score():
    '''
    La idea de esta función no es que deseche documentos, sino que haga una lectura rápida del abstracto y que considere un criterio
    del usuario, para realizar una sugerencia, de esa manera el usuario podría tener prioridad para ciertos textos
    '''
    return 0


def pandas_to_excel(df, nombre):
    '''
    Para pasar cualquier documento de pandas a excel, crea un archivo excel e el directorio con el nombre
    '''
    df.to_excel(nombre, index=True)
    return ('Finalizado parte 2')


