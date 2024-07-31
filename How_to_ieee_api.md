## Sobre los parametros:

En la API de IEEE Xplore, puedes utilizar varios parámetros para personalizar tus búsquedas y obtener resultados más precisos. Aquí tienes una lista de algunos de los parámetros más importantes y cómo se pueden utilizar:

- querytext: Realiza una búsqueda de texto libre en todos los campos de metadatos configurados y en el texto del documento. Este parámetro acepta consultas complejas que pueden incluir nombres de campos y operadores booleanos.

- abstract: Busca dentro de los resúmenes de los artículos.

- affiliation: Busca artículos escritos por autores afiliados a una organización específica.

- article_number: El identificador único de IEEE para un artículo específico. Si se utiliza este parámetro, se ignoran todos los demás parámetros.

- article_title: Busca por el título de un documento individual (artículo de revista, conferencia, estándar, capítulo de libro, o curso).

- author: Busca por el nombre de un autor. Requiere un mínimo de tres caracteres precediendo el comodín (*).

- doi: El identificador único asignado a un artículo/documento por CrossRef. Si se incluye este parámetro, se ignoran todos los demás parámetros excepto article_number.

- publication_title: Busca por el título de una publicación (revista, conferencia, o estándar).

- publication_year: Especifica el año de publicación.

- start_date y end_date: Permiten buscar documentos publicados dentro de un rango específico de fechas.

- start_record: Utilizado para paginación, especifica el punto de inicio para devolver resultados.

- d-au: Faceta de autor abierta; los resultados contienen un enlace de refinamiento que devuelve todos los documentos de un autor dado relevantes para esa búsqueda.

- d-publisher: Faceta de editor; los resultados contienen un enlace de refinamiento que devuelve todos los documentos de un editor dado relevantes para esa búsqueda.

- d-pubtype: Faceta de tipo de contenido; los resultados contienen un enlace de refinamiento que devuelve todos los documentos de un tipo de contenido dado relevantes para esa búsqueda.

- d-year: Faceta de año de publicación.