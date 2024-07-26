import requests

# Función para construir la URL de la API de IEEE Xplore
def build_ieee_xplore_url(api_key, query, max_records=10):
    base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    params = {
        'apikey': api_key,
        'querytext': query,
        'max_records': max_records
    }
    return base_url, params

# Función para realizar la solicitud a la API de IEEE Xplore
def search_ieee_xplore(api_key, query, max_records=10):
    base_url, params = build_ieee_xplore_url(api_key, query, max_records)
    
    # Realizar la solicitud GET a la API
    response = requests.get(base_url, params=params)
    # Contador para prueba, borrar contador y el break
    i=0
    
    # Verificar el estado de la respuesta
    if response.status_code == 200:
        # Parsear la respuesta JSON
        data = response.json()
        
        # Procesar los resultados
        for article in data.get('articles', []):
            title = article.get('title', 'No Title')
            authors = article.get('authors', 'No Authors')
            abstract = article.get('abstract', 'No Abstract')
            publication_date = article.get('publication_date', 'No Date')
            journal = article.get('publication_title', 'No Journal')
            
            print(f"Title: {title}")
            print(f"Authors: {authors}")
            print(f"Abstract: {abstract}")
            print(f"Publication Date: {publication_date}")
            print(f"Journal: {journal}")
            print("-" * 40)

            # aumentando contador
            i+=1

            if i<5:
                break

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Tu clave API de IEEE Xplore
API_KEY = '75wksqxp5nhr3accjbtfk8bj'

# Parámetros de búsqueda
query = 'machine learning'
max_results = 10

# Realizar la búsqueda
search_ieee_xplore(API_KEY, query, max_results)