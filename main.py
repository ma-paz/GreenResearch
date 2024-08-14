import requests
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel 
from Processing_layer_funcs import *
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

app = FastAPI()

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
        'start_year' : year,
        'end_year' : current_year
    }
    return base_url, params

# Función para realizar la solicitud a la API de IEEE Xplore
def search_ieee_xplore(api_key, query, max_records, min_year):
    base_url, params = build_ieee_xplore_url(api_key, query, max_records, min_year)
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        datos = {
            "Title": [],
            "Authors": [],
            "Abstract": [],
            "Publication Date": [],
            "Journal": [],
            "DOI": [],
            "Citations": []
        }
        for article in data.get('articles', []):
            datos["Title"].append(article.get('title', 'No Title'))
            datos["Authors"].append(article.get('authors', 'No Authors'))
            datos["Abstract"].append(article.get('abstract', 'No Abstract'))
            datos["Publication Date"].append(article.get('publication_date', 'No Date'))
            datos["Journal"].append(article.get('publication_title', 'No Journal'))
            datos["DOI"].append(article.get('doi', 'No DOI'))
            datos["Citations"].append(article.get('citing_paper_count', 'No Citations'))
        
        df = pd.DataFrame(datos)
        return df
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Error: {response.text}")

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

class RequestModel(BaseModel):
    query: str
    min_year: str
    context: str
    avoided: str

@app.post("/process")
def process_request(request: RequestModel):
    query = request.query
    min_year = request.min_year
    context = request.context
    avoided = request.avoided
    max_results = 500
    
    # Proceso de generación de nuevas queries
    instructions_triggers = 'I will give you a list of concepts on topics and i need you to expand said list and add synonyms of these concepts, no explanation just the term . Only give me the list, no extra text allowed. Format of the list should be a string in the format: concept1, concept2, concept3'
    list_of_triggers = smart_prompt_assistant(instructions_triggers + "\n\n" + avoided)
    list_of_triggers = list_of_triggers.strip('\n').split(',')

    nuevo_contexto = Get_topic(context)

    instructions_1 = 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees 3 titulos alternos y las concatenes con el operador logico OR. Ejemplo de como espero que se vea la respuesta: mobile programming OR smartphone programming OR smartphone app developemet. Es importante que solo me respondas en el formato del ejemplo. A continuación te entrego la query que quiero que proceses:'
    new_query1 = smart_prompt_assistant(instructions_1 + "\n\n" + query)

    instructions_2 = 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees un prompt alternativo, que consista en un termino alternativo al query original y enlaces a través del operador logico NEAR un termino básado en el contexto que se te entregará después. Ejemplo de formato de resultado: smartphone NEAR/6 sustainability.Es importante que solo me respondas en el formato del ejemplo. Query original: '
    new_query2 = smart_prompt_assistant(instructions_2 + query + "\n\n Contexto:" + nuevo_contexto)

    instructions_3 = 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees una query alternativa con synonimos y el mismo formato, para ello se te entregará la query origninal, un contexto y temas que no quiero en la búsqueda. Es importante que solo me respondas con la nueva query.'
    new_query3 = smart_prompt_assistant(instructions_3 + "\n query original" + new_query1 + "\n\n" + "contexto:" + nuevo_contexto + "\n temas a evitar:" + '-'.join(list_of_triggers))

    # Realizar la búsqueda
    df1 = search_ieee_xplore(ieee_api_key, new_query1, max_results, min_year)
    df2 = search_ieee_xplore(ieee_api_key, new_query2, max_results, min_year)
    df3 = search_ieee_xplore(ieee_api_key, new_query3, max_results, min_year)
    new_df = pd.concat([df1, df2, df3], ignore_index=True)
    
    filtro_aplicado = procesar_texto(new_df, new_query1, nuevo_contexto, list_of_triggers)[0]
    filtro_doi_aplicado = drop_rows_without_doi(filtro_aplicado)

    # Guardar el resultado en un archivo Excel
    output_filename = 'output_filtrado.xlsx'
    filtro_doi_aplicado.to_excel(output_filename, index=False)
    
    return FileResponse(output_filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=output_filename)
# Para levantar el servidor, puedes usar el siguiente comando
# uvicorn main:app --reload