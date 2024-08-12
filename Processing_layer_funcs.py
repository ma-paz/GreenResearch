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

#Quiero una función para determinar el topico de investigación en codewords, para ello utilizaré ai y así puedo refinar el proceso de filtrado
def Get_topic(contexto, tokens=100, model="gpt-3.5-turbo"):
    client = OpenAI()
    who= 'You are a helptful assistant'#lo hago así para leerlo bien en caso de editarlo en el futuro
    
    prompt= 'A continuación se te presenta un fragmento escrito por el investigador, el investigador declara ahí los objetivos y el contexto de su busqueda. Necesito que me entregues una lista de topicos que describan la búsqueda del investigador:'+ contexto + 'El formato de salida debe ser solo la lista. Ej: topico_1, topico_2, topico_3. La respuesta debe estar en ingles siempre' 
    
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
        resultado=(response.choices[0].message.content)
        return resultado
    except Exception as e:
        return f"Error: {e}"


#Función que conecta a las palabras del filtro 
def Seleccionar_outliers(lista_completa, original_prompt, contexto, tokens=100, model="gpt-4o"):
    
    '''Escribir función que ayuda a seleccionar outliers, 
    considerar la necesidad de incorporar la voluntad del usuario, posible ayuda de ia
    '''
    client = OpenAI()
    who= 'You are a helptful assistant for data analysis.'#lo hago así para leerlo bien en caso de editarlo en el futuro
    I1='I want you to create a list of words that have NOTHING to do with a particular topic or theme.\n' 
    I2='\n Here is the original topic :\n' 
    I3='\n And this is the list of which you will select the unrelated words: \n'
    #I4='\n Now, this is a bit of context to help you find these words that have nothing to do with the topic or the context: '
    I4='\n Now, this is a bit of context. The following is a small list of themes that give context to the original topic: '
    I5='Finally, is an example of the format i want for the answer (use this format and nothing else)(i want the words divided by a coma): Cities, Iot, Cloud, Hardware\n\n'

    #prompt=I1 + I2 + original_prompt+ I3+ ','.join(lista_completa)+ I4 + contexto + I5
    prompt= 'I give you a list of words present in a bunch of titles:'+ ','.join(lista_completa)+'\n\n I want you to give me back a list of the words in that list, that might indicate the presence of a totally unrelated topic to the context given(ignore dates and numbers)(remember words that talk about other topics not contained in the context given). The context in question:\n' + contexto +'\n Important: write the list and nothing else.'
    
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
        resultado=(response.choices[0].message.content).strip('\n').replace(" ","").split('\n-')[0].split(',')
        return resultado
    except Exception as e:
        return f"Error: {e}"
        

#Función que saca elementos repetidos de una columna por outliers
def Filtrar_outliers(documento, lista_outliers, abstracto_o_titulo):
    '''
    abstracto_o_titulo:
    1 = Abstract
    * = Title
    '''
    if abstracto_o_titulo != 1:
        columna = 'Title'
    else:
        columna = 'Abstract'

    # Convert the column to a string type to ensure .str accessor works
    documento.loc[:, columna] = documento[columna].astype(str)
    
    print(f"Filtering column: {columna}")
    print(f"Outliers list: {lista_outliers}")
    
    # Apply the filter
    filtered_documento = documento[~documento[columna].str.contains('|'.join(lista_outliers), case=False, na=False)]
    
    print(f"Shape after filtering: {filtered_documento.shape}")
    
    return filtered_documento

def procesar_texto(df, query, nuevo_contexto, list_of_triggers):
    """
    Procesa el DataFrame para filtrar por abstracto y título usando criterios específicos.

    Parámetros:
    - df: DataFrame original a procesar.
    - query: Criterios de búsqueda o consulta.
    - nuevo_contexto: Contexto utilizado para seleccionar palabras outliers.
    - list_of_triggers: Lista de palabras que se utilizan como filtro adicional.

    Retorna:
    - forma_final: DataFrame filtrado y sin duplicados.
    """
    # Quitar duplicados
    df = quitar_duplicados(df)

    # Creando filtro y filtrando por abstracto
    list_abs = palabras_columna(df, 1)
    bad_words_abs = Seleccionar_outliers(list_abs, query, nuevo_contexto)
    filtro_aplicado = Filtrar_outliers(df, bad_words_abs, 1)
    filtro_aplicado = Filtrar_outliers(filtro_aplicado, list_of_triggers, 1)

    # Creando filtro y filtrando por título
    list_tit = palabras_columna(filtro_aplicado, 0)
    bad_words_tit = Seleccionar_outliers(list_tit, query, nuevo_contexto)
    forma_final = Filtrar_outliers(filtro_aplicado, bad_words_tit, 0)
    forma_final = Filtrar_outliers(forma_final, list_of_triggers, 0)

    # Evitar copias por procesamiento
    forma_final = forma_final.drop_duplicates()

    # Mostrar forma final
    print(forma_final.shape)

    return forma_final,bad_words_abs,bad_words_tit

def drop_rows_without_doi(df, doi_column='DOI'):
    """
    Drops all rows from the DataFrame that don't have a DOI.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    doi_column (str): The name of the column containing DOIs. Default is 'DOI'.

    Returns:
    pd.DataFrame: The DataFrame with rows without a DOI removed.
    """
    # Drop rows where the DOI column is None or NaN
    df = df.dropna(subset=[doi_column])

    # Drop rows where the DOI column is an empty string
    df = df[df[doi_column].str.strip() != '']

    return df


def label_documents_with_keyword(df, terms, api_key):
    """
    Labels each document in the DataFrame with the terms found in the document topics.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing a column 'DOI' with the DOI of each document.
    terms (list): List of terms to search for in the document topics.
    api_key (str): IEEE Xplore API key.
    
    Returns:
    pd.DataFrame: Original DataFrame with an additional column 'Found_Terms'
                 listing the terms found in each document's topics.
    """
    results = []

    for doi in df['DOI']:
        # Define the API request parameters
        url = "https://api.xplore.ieee.org/api/v1/documents"
        params = {
            "apikey": api_key,
            "format": "json",
            "doi": doi,
            "fields": "index_terms,controlled_terms,uncontrolled_terms"
        }

        # Make the API request
        response = requests.get(url, params=params)
        data = response.json()

        # Extract the terms
        index_terms = data.get('index_terms', {}).get('ieee_terms', [])
        author_terms = data.get('index_terms', {}).get('author_terms', [])
        controlled_terms = data.get('controlled_terms', [])
        uncontrolled_terms = data.get('uncontrolled_terms', [])

        # Combine all terms into one list and convert to lowercase
        all_terms = [t.lower() for t in index_terms + author_terms + controlled_terms + uncontrolled_terms]

        # Find which of the specified terms are present
        found_terms = [term for term in terms if term.lower() in all_terms]

        # If terms are found, join them into a string, otherwise leave the field empty
        results.append(', '.join(found_terms) if found_terms else 'None')

    # Add the results as a new column to the DataFrame
    df['Found_Terms'] = results

    return df
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


