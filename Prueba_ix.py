import requests
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
from Processing_layer_funcs import *
import pandas as pd
from datetime import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()
ieee_api_key = os.getenv('IEEE_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
current_year = datetime.now().year

# Función para construir la URL de la API de IEEE Xplore
def build_ieee_xplore_url(api_key, query, max_records, year):
    base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    params = {
        'apikey': api_key,
        'querytext': query,
        'max_records': max_records,
        'd-year' : year
    }
    return base_url, params

# Función para realizar la solicitud a la API de IEEE Xplore
def search_ieee_xplore(api_key, query, max_records, min_year):
    base_url, params = build_ieee_xplore_url(api_key, query, max_records, min_year)
    
    # Realizar la solicitud GET a la API
    response = requests.get(base_url, params=params)
    
    # Verificar el estado de la respuesta
    if response.status_code == 200:
        # Parsear la respuesta JSON
        data = response.json()
        
        # Inicializar un diccionario para almacenar los datos
        datos = {
            "Title": [],
            "Authors": [],
            "Abstract": [],
            "Publication Date": [],
            "Journal": [],
            "DOI": [],
            "Citations": []
        }
        
        # Procesar los resultados
        for article in data.get('articles', []):
            datos["Title"].append(article.get('title', 'No Title'))
            datos["Authors"].append(article.get('authors', 'No Authors'))
            datos["Abstract"].append(article.get('abstract', 'No Abstract'))
            datos["Publication Date"].append(article.get('publication_date', 'No Date'))
            datos["Journal"].append(article.get('publication_title', 'No Journal'))
            datos["DOI"].append(article.get('doi', 'No DOI'))
            datos["Citations"].append(article.get('citing_paper_count', 'No Citations'))
        
        # Crear un DataFrame de pandas a partir del diccionario
        df = pd.DataFrame(datos)
        
        # Escribir el DataFrame en un archivo Excel
        df.to_excel('output.xlsx', index=False)

        print("Datos guardados en 'output.xlsx'")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    return df


# Función para consultar a la API de OpenAI GPT
def smart_prompt_assistant(prompt, model="gpt-3.5-turbo", max_tokens=100):
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are prompt assistant for ieee xplore prompts."},
                {"role": "user", "content": prompt}
            ],max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def Buscando_fecha(api_key, query, max_records, year):
    '''
    Función que realiza el llamado por año desde el año entregado hasta el presente.
    '''
    
    return 0





# Ingreso de información del usuario
query = input('Ingresa tu query: ')
min_year = input('Ingresa una fecha minima de búsqueda: ')# ver que pasa con la variable
context = input('Ingresa un parrafo que indique el objetivo de esta investigación: ')
max_results = 5000 #Este número se puede ajustar a voluntad, estoy buscando algún lado con un argumento logico

# Instrucciones para openAI y la actualización de la query para ieee xplore
instructions= 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees 3 titulos alternos y las concatenes con el operador logico OR. Ejemplo de como espero que se vea la respuesta: mobile programming OR smartphone programming OR smartphone app developemet. Es importante que solo me respondas en el formato del ejemplo. A continuación te entrego la query que quiero que proceses:'
new_query = smart_prompt_assistant(instructions + "\n\n" + query)
#sin llamar por que no quiero gastar mis creditos
# Piensa que la instrucción de openAI puede ser modificada para obtener mejor resultados, ahí hay un trabajo que hacer. Como saber que es una query optima de busqueda, como evaluamos la calidad de la query por ejemplo
print(new_query)


# Realizar la búsqueda
df=search_ieee_xplore(ieee_api_key, new_query, max_results, min_year)

#Procesamiento de texto
df= quitar_duplicados(df)
list_abs = palabras_columna(df, 1)
bad_words_abs = Seleccionar_outliers_small(list_abs,query,context)
filtro_aplicado= Filtrar_outliers(df,bad_words_abs,1)
list_tit = palabras_columna(df, 0)
bad_words_tit = Seleccionar_outliers_small(list_tit,query,context)
filtro_aplicado= Filtrar_outliers(filtro_aplicado,bad_words_tit,0)
print("RESULTADO")
print(filtro_aplicado)
#pandas_to_excel(df,'Prueba_filtro_abstracto')
