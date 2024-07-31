from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import json
import time
from webdriver_manager.chrome import ChromeDriverManager

# Configuración de Selenium y ChromeDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless
#chrome_service = Service(executable_path='C:/Users/mari_/OneDrive/Escritorio/chromedriver-win64/chromedriver.exe')  # Asegúrate de que esta ruta es correcta

# Iniciar el WebDriver
driver = webdriver.Chrome(executable_path='C:/Users/mari_/OneDrive/Escritorio/chromedriver-win64/chromedriver.exe', options=chrome_options)

# URL de búsqueda
def make_url(search,min_year,max_year):
    search=search.strip().split()
    search_url= "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText="
    search_url += '%20'.join(search)
    search_url+="&highlight=true&returnType=SEARCH&matchPubs=true&openAccess=true&returnFacets=ALL&ranges="
    search_url+=str(min_year)+'_'+str(max_year)+'_Year'
    return search_url

# Función para extraer DOIs usando Selenium
# Función para extraer DOIs usando Selenium
def extract_dois(search_url):
    driver.get(search_url)
    
    # Esperar explícitamente a que los elementos estén presentes
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.List-results-items .result-item-title a'))
        )
    except:
        print("Error: Elementos no encontrados.")
        return []

    # Imprimir el HTML de la página cargada para verificar que el contenido está presente
    page_html = driver.page_source
    print(page_html)

    items = driver.find_elements(By.CSS_SELECTOR, '.List-results-items .result-item-title a')
    print(f"Items encontrados: {len(items)}")

    dois = []
    for item in items:
        href = item.get_attribute('href')
        if '/document/' in href:
            doi = href.split('/')[-1]
            dois.append(doi)

    return dois

# Función para descargar detalles de un documento
def download_doc(doi):
    doc_url = f'https://ieeexplore.ieee.org/document/{doi}'
    driver.get(doc_url)
    time.sleep(5)  # Esperar a que la página cargue completamente

    title = driver.find_element(By.CSS_SELECTOR, 'h1.document-title').text
    authors = [author.text for author in driver.find_elements(By.CSS_SELECTOR, 'a.author-name')]
    abstract = driver.find_element(By.CSS_SELECTOR, 'div.abstract-text').text
    references = []
    cited_by = []

    # Extraer referencias
    ref_items = driver.find_elements(By.CSS_SELECTOR, 'div.references__item a')
    for ref in ref_items:
        ref_href = ref.get_attribute('href')
        if 'doi.org' in ref_href:
            references.append(ref_href.split('/')[-1])

    # Extraer citas
    cited_by_items = driver.find_elements(By.CSS_SELECTOR, 'div.citedBySection a')
    for cited_by_item in cited_by_items:
        cited_by_href = cited_by_item.get_attribute('href')
        if 'doi.org' in cited_by_href:
            cited_by.append(cited_by_href.split('/')[-1])

    doc = {
        'title': title,
        'authors': ', '.join(authors),
        'abstract': abstract,
        'references': references,
        'citedby': cited_by
    }
    
    return doc

# Guardar documento en la base de datos SQLite
DB_NAME = 'docs.db'

def save_doc(uid, doc):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('INSERT INTO docs (uid, doc) VALUES (?, ?)', (uid, json.dumps(doc, ensure_ascii=False)))
    con.commit()
    con.close()

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

def print_docs(docs):
    for uid, doc in docs:
        print(f"UID: {uid}")
        print(f"Title: {doc.get('title', 'No Title')}")
        print(f"Authors: {doc.get('authors', 'No Authors')}")
        print(f"Abstract: {doc.get('abstract', 'No Abstract')}")
        print(f"References: {len(doc.get('references', []))}")
        print(f"Cited By: {len(doc.get('citedby', []))}")
        print("-" * 40)

# Armar la URL
search = input("Ingrese su búsqueda: ")
min_year = input("Año mínimo: ")
max_year = 2024
search_url = make_url(search, min_year, max_year)

# Realizar la búsqueda y obtener los DOIs
create_table()
dois = extract_dois(search_url)

# Descargar y guardar documentos
for doi in dois:
    print(f'Descargando DOI: {doi}')
    doc = download_doc(doi)
    save_doc(doi, doc)
    print(f'Documento {doi} guardado.')

print('Proceso completado.')
driver.quit()

# Leer y imprimir los documentos
docs = read_docs()
print_docs(docs)
print("docs impresos")

