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

def make_chrome_headless(executable_p):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(executable_path=executable_p, options=options)
    return driver

# Configuración del WebDriver
executable_path = 'C:/Users/mari_/OneDrive/Escritorio/chromedriver-win64/chromedriver.exe'
driver = make_chrome_headless(executable_path)

def make_url(search, min_year, max_year):
    search_terms = search.split()
    search_url = "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText="
    search_url += '%20'.join(search_terms)
    search_url += "&highlight=true&returnType=SEARCH&matchPubs=true&openAccess=true&returnFacets=ALL&ranges="
    search_url += str(min_year) + '_' + str(max_year) + '_Year'
    return search_url

def extract_dois(search_url):
    driver.get(search_url)
    
    # Esperar explícitamente a que los elementos estén presentes
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.List-results-items'))
        )
    except Exception as e:
        print("Error: Elementos no encontrados.")
        print(e)
        return []

    # Obtener el HTML de la página para verificar la estructura
    page_source = driver.page_source
    with open('page_source.html', 'w', encoding='utf-8') as file:
        file.write(page_source)

    items = driver.find_elements(By.CSS_SELECTOR, '.List-results-items .result-item-title a')
    print(f"Items encontrados: {len(items)}")
    print(items)

    dois = []
    for item in items:
        href = item.get_attribute('href')
        if '/document/' in href:
            doi = href.split('/')[-1]
            dois.append(doi)

    return dois


# Generar la URL de búsqueda
search = "green coding"
min_year = 2020
max_year = 2024
search_url = make_url(search, min_year, max_year)
print(f"URL de búsqueda: {search_url}")

# Realizar la búsqueda y obtener los DOIs
dois = extract_dois(search_url)

for doi in dois:
    print(f'DOI: {doi}')

print('Proceso completado.')
driver.quit()