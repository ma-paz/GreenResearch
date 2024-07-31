import requests
from bs4 import BeautifulSoup
import json
import sqlite3

# URL de búsqueda
def make_url(search,min_year,max_year):
    search=search.split()
    search_url= "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText="
    for palabra in search:
        search_url+=palabra+'%%'
    search_url+="&highlight=true&returnType=SEARCH&matchPubs=true&openAccess=true&returnFacets=ALL&ranges="
    search_url+=search_url+str(min_year)+'_'+str(max_year)+'_Year'
    return search_url


# Función para realizar una solicitud y obtener el contenido de la página
def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    return response.content

# Función para extraer DOIs de los resultados de búsqueda
def extract_dois(content):
    soup = BeautifulSoup(content, 'html.parser')
    print(soup)
    doi_list = []
    for item in soup.find_all('div', class_='List-results-items'):
        a_tag = item.find('a', href=True)
        #print(a_tag)
        if a_tag:
            href = a_tag['href']
            if '/document/' in href:
                doi = href.split('/')[-1]
                doi_list.append(doi)
    #print(doi_list)
    return doi_list

# Función para descargar detalles de un documento
def download_doc(doi):
    doc_url = f'https://ieeexplore.ieee.org/document/{doi}'
    content = get_page_content(doc_url)
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extraer el título del documento
    title_tag = soup.find('h1', class_='document-title')
    title = title_tag.get_text(strip=True) if title_tag else 'No Title'
    
    # Extraer autores
    authors = []
    for author in soup.find_all('a', class_='author-name'):
        authors.append(author.get_text(strip=True))
    
    # Extraer abstract
    abstract_tag = soup.find('div', class_='abstract-text')
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else 'No Abstract'
    
    # Extraer referencias
    references = []
    for ref in soup.find_all('div', class_='references__item'):
        ref_link = ref.find('a', href=True)
        if ref_link and 'doi.org' in ref_link['href']:
            references.append(ref_link['href'].split('/')[-1])
    
    # Extraer citas (citado por)
    cited_by = []
    cbu_tag = soup.find('a', {'data-ajaxurl': True})
    if cbu_tag and '/action/ajaxShowCitedBy' in cbu_tag['data-ajaxurl']:
        cbu_url = 'https://ieeexplore.ieee.org' + cbu_tag['data-ajaxurl']
        cbu_content = get_page_content(cbu_url)
        cbu_soup = BeautifulSoup(cbu_content, 'html.parser')
        for cite in cbu_soup.find_all('a', href=True):
            if 'doi.org' in cite['href']:
                cited_by.append(cite['href'].split('/')[-1])
    
    doc = {
        'title': title,
        'authors': ', '.join(authors),
        'abstract': abstract,
        'references': references,
        'citedby': cited_by
    }
    
    return doc

# Guardar documento en la base de datos SQLite
def save_doc(uid, doc):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('INSERT INTO docs (uid, doc) VALUES (?, ?)', (uid, json.dumps(doc, ensure_ascii=False)))
    con.commit()
    con.close()

# Nombre de la base de datos
DB_NAME = 'docs.db'

# Crear tabla si no existe
def create_table():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS docs (uid TEXT NOT NULL PRIMARY KEY, doc TEXT NOT NULL)')
    con.commit()
    con.close()


def read_docs():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('SELECT uid, doc FROM docs')
    
    docs = []
    for row in cur.fetchall():
        uid = row[0]
        doc = json.loads(row[1])
        docs.append((uid, doc))
    
    con.close()
    return docs
""""""
def print_docs(docs):
    for uid, doc in docs:
        print(f"UID: {uid}")
        print(f"Title: {doc.get('title', 'No Title')}")
        print(f"Authors: {doc.get('authors', 'No Authors')}")
        print(f"Abstract: {doc.get('abstract', 'No Abstract')}")
        print(f"References: {len(doc.get('references', []))}")
        print(f"Cited By: {len(doc.get('citedby', []))}")
        print("-" * 40)



# Realizar la búsqueda y obtener los DOIs
search=input("ingrese su busqueda")
min_year=input("año minimo")
max_year=2024
search_url= make_url(search,min_year,max_year)
content = get_page_content(search_url)
dois = extract_dois(content)

# Crear tabla en la base de datos
create_table()

# Descargar y guardar documentos
for doi in dois:
    print(f'Descargando DOI: {doi}')
    doc = download_doc(doi)
    save_doc(doi, doc)
    print(f'Documento {doi} guardado.')

print('Proceso completado.')

# Leer y imprimir los documentos
docs = read_docs()
print_docs(docs)
