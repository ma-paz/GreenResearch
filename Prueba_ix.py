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
    '''
    Esta función solo crea los parametros para realizar la consulta a ieeexplore
    '''
    base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    params = {
        'apikey': api_key,
        'querytext': query,
        'max_records': max_records,
        'start_year' : year,
        'end_year' : current_year
    }
    return base_url, params

# Función para realizar la solicitud a la API de IEEE Xplore
def search_ieee_xplore(api_key, query, max_records, min_year):
    '''
    Función que hace la consulta a ieee xplore. Genera un file .xlsx bajo el nombre de 'output' y aparte retorna un dataFrame.
    '''
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





# Ingreso de información del usuario
query = input('Ingresa tu query: ')
min_year = input('Ingresa una fecha minima de búsqueda: ')# ver que pasa con la variable
context = input('Ingresa un parrafo que indique el objetivo de esta investigación: ')
avoided = input('Ingresa elementos del área que quieras evitar, en formato de palabras o terminos: ')
max_results = 500 #Este número se puede ajustar a voluntad, estoy buscando algún lado con un argumento logico


#new query genera un string más largo con titulos alternativos para ampliar el área de búsquda
instructions_triggers= 'I will give you a list of words on topics and i need you to create a list with these words and add to the list their synonyms. Only give me the list, no extra text allowed.'
list_of_triggers= smart_prompt_assistant(instructions_triggers + "\n\n" + avoided)
list_of_triggers=list_of_triggers.strip('\n').split('\n-')

#nuevo_contexto genera una lista en formato str donde se describen los tópicos definidos por el usuario, que serán utilizados como criterio de exclusión
nuevo_contexto=Get_topic(context)
print('\nNuevo contexto: '+nuevo_contexto.strip(' '))

# Instrucciones para openAI y la actualización de la query para ieee xplore
instructions= 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees 3 titulos alternos y las concatenes con el operador logico OR. Ejemplo de como espero que se vea la respuesta: mobile programming OR smartphone programming OR smartphone app developemet. Es importante que solo me respondas en el formato del ejemplo. A continuación te entrego la query que quiero que proceses:'
new_query1 = smart_prompt_assistant(instructions + "\n\n" + query)
instructions= 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees un prompt alternativo, que consista en un termino alternativo al query original y enlaces a través del operador logico NEAR un termino básado en el contexto que se te entregará después. Ejemplo de formato de resultado: smartphone NEAR/6 sustainability.Es importante que solo me respondas en el formato del ejemplo. Query original: '
new_query2 = smart_prompt_assistant(instructions + query + "\n\n Contexto:"+ nuevo_contexto)
instructions= 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees una query alternativa con synonimos y el mismo formato, para ello se te entregará la query origninal, un contexto y temas que no quiero en la búsqueda. Es importante que solo me respondas con la nueva query.'
new_query3 = smart_prompt_assistant(instructions + "\n query original" + new_query1 +"\n\n"+"contexto:"+nuevo_contexto+ "\n temas a evitar:"+ '-'.join(list_of_triggers))

print('Query 1:'+new_query1+'\n Query 2:'+new_query2+'\n Query 3: '+new_query3)
# Piensa que la instrucción de openAI puede ser modificada para obtener mejor resultados, ahí hay un trabajo que hacer. Como saber que es una query optima de busqueda, como evaluamos la calidad de la query por ejemplo



# Realizar la búsqueda
df1=search_ieee_xplore(ieee_api_key, new_query1, max_results, min_year)
df2=search_ieee_xplore(ieee_api_key, new_query2, max_results, min_year)
df3=search_ieee_xplore(ieee_api_key, new_query3, max_results, min_year)
new_df = pd.concat([df1, df2, df3], ignore_index=True)
print(new_df.shape)
print(df1.shape)
print(df2.shape)
print(df3.shape)


filtro_aplicado=procesar_texto(new_df,new_query1,nuevo_contexto,list_of_triggers)[0]
filtro_doi_aplicado=drop_rows_without_doi(filtro_aplicado)


# Escribir el DataFrame en un archivo Excel
filtro_doi_aplicado.to_excel('output_filtrado.xlsx', index=False)

#Mostrar copias
#print("RESULTADO")
#print(filtro_aplicado)
#pandas_to_excel(df,'Prueba_filtro_abstracto')
