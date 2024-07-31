import requests
import os
import openai
from dotenv import load_dotenv
from openai import OpenAI
import csv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Función para construir la URL de la API de IEEE Xplore
def build_ieee_xplore_url(api_key, query, max_records, min_year):
    base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    params = {
        'apikey': api_key,
        'querytext': query,
        'max_records': max_records,
        'start_date' : int(min_year)
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
        # Abrir archivo CSV para escritura
        with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Authors', 'Abstract', 'Publication Date', 'Journal', 'DOI', 'Citations'])
            
            # Procesar los resultados
            for article in data.get('articles', []):
                title = article.get('title', 'No Title')
                authors = article.get('authors', 'No Authors')
                abstract = article.get('abstract', 'No Abstract')
                publication_date = article.get('publication_date', 'No Date')
                journal = article.get('publication_title', 'No Journal')
                doi = article.get('doi', 'No DOI')
                citations = article.get('citing_paper_count', 'No Citations')
                
                writer.writerow([title, authors, abstract, publication_date, journal, doi, citations])

    else:
        print(f"Error: {response.status_code}")
        print(response.text)



# Función para consultar a la API de OpenAI GPT
def query_openai(prompt, model="gpt-3.5-turbo", max_tokens=100):
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


# Tu clave API de IEEE Xplore
ieee_api_key = os.getenv('IEEE_API_KEY')
# Configura tu clave API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Parámetros de búsqueda
query = input('Ingresa tu query: ')
min_year = input('Ingresa una fecha minima de búsqueda: ')
max_results = 50

# Instrucciones para openAI y la actualización de la query para ieee xplore
instructions= 'Te entregaré una query que es originalmente pensada para la herramienta de busqueda IEEE xplore. Necesito que crees 3 titulos alternos y las concatenes con el operador logico OR. Ejemplo de como espero que se vea la respuesta: "mobile programming" OR "smartphone programming" OR "smartphone app developemet". A continuación te entrego la query que quiero que proceses'
#new_query = query_openai(instructions + "\n\n" + query)
#sin llamar por que no quiero gastar mis creditos
#print(new_query)


# Realizar la búsqueda
#search_ieee_xplore(ieee_api_key, new_query, max_results)
search_ieee_xplore(ieee_api_key, query, max_results, min_year)