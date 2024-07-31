import pandas as pd
import os
import numpy as np
from collections import Counter

#Función para quitar los clones de un pandas array
def quitar_duplicados(datos):
    return datos.drop_duplicates()

#Función que recolecta una lista con todas las palabras que encontramos en una columna
def palabras_columna(dataframe, abstracto_o_titulo):
    '''
    abstracto_o_titulo:
    1=abstracto
    *=titulo
    '''
    # Tokenización y recuento de palabras en todas las descripciones
    if abstracto_o_titulo!=1:
        palabras = ' '.join(dataframe['Title']).split()
    else:
        palabras = ' '.join(dataframe['Abstract']).split()

    conteo_palabras = Counter(palabras)

    # Identificación de palabras repetidas
    palabras_repetidas = [palabra for palabra, conteo in conteo_palabras.items() if conteo > 1]

    # Lista de palabras de conexión o relleno a excluir
    skip = ['is', 'in', 'else', 'or', 'we', 'We', 'the', 'to', 'a', 'on', 'that', 'with', 'The', 'as', 'are', '(', ')', 'than', 'elsewhere', 'and', 'of', 'for', 'However,', '…', 'but', 'however', 'therefore', 'moreover', 'furthermore', 'meanwhile', 'nevertheless', 'hence', 'thus', 'although', 'even though', 'despite', 'in addition', 'nonetheless', 'on the other hand', 'as a result', 'likewise', 'similarly']

    # Agregando las palabras repetidas a una lista
    lista = [palabra for palabra in palabras_repetidas if palabra not in skip]#mejorar esta función el conteo es innecesario

    return lista
#Función que conecta a las palabras del filtro 
def Seleccionar_outliers(lista_completa):
    #Escribir función que ayuda a seleccionar outliers, considerar la necesidad de incorporar la voluntad del usuario, posible ayuda de ia
    return 0

#Función que saca elementos repetidos de una columna por outliers
def Filtrar_outliers(documento, lista_outliers, abstracto_o_titulo):
    '''
    abstracto_o_titulo:
    1=abstracto
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
    del usuario, para realizar una sugerencia, de esa manera el usuario podría tener prioridad para ciertos textos'''
    return 0


