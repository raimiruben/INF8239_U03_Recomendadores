# Dataset Card · MovieLens

## Fuente, fecha, versión y hash
- **Fuente:** GroupLens Research, University of Minnesota. Conjunto *MovieLens Latest Small* (`ml-latest-small`).
- **URL de descarga:** https://files.grouplens.org/datasets/movielens/ml-latest-small.zip (configurable con la variable `MOVIELENS_URL`).
- **Versión:** el README oficial indica que el conjunto se generó el 26 de septiembre de 2018. GroupLens lo describe como un conjunto de desarrollo que puede cambiar con el tiempo y no lo recomienda para resultados científicos compartidos; por eso se registra el hash de los bytes descargados.
- **Fecha de descarga:** 2026-10-17.
- **SHA-256 del archivo zip descargado:** `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` (calculado por `scripts/download_data.py`).

## Licencia y cita
Uso académico y de investigación bajo las condiciones del README oficial de GroupLens:
1. No sugerir que la Universidad de Minnesota o GroupLens avalan este trabajo.
2. Citar el conjunto en las publicaciones derivadas.
3. Se puede redistribuir, incluidas versiones modificadas, bajo las mismas condiciones.
4. El uso comercial o con fines de lucro requiere permiso previo de un profesor de GroupLens.

Los datos se ofrecen sin garantías de exactitud ni de idoneidad para un fin concreto.

Harper, F. M., & Konstan, J. A. (2015). The MovieLens Datasets: History and Context. ACM Transactions on Interactive Intelligent Systems, 5(4). DOI: 10.1145/2827872.

## Archivos y diccionario
| Archivo | Campos | Uso en el proyecto |
|---|---|---|
| `ratings.csv` | `userId`, `movieId`, `rating` (0,5 a 5,0 en pasos de 0,5), `timestamp` (segundos Unix) | Popularidad, factorización y evaluación |
| `movies.csv` | `movieId`, `title` (incluye el año), `genres` (géneros separados por `|`) | Catálogo y recomendador por contenido |
| `tags.csv` | `userId`, `movieId`, `tag`, `timestamp` | No se usa en este laboratorio |
| `links.csv` | `movieId`, `imdbId`, `tmdbId` | No se usa en este laboratorio |

## Procedimiento de descarga
`uv run python scripts/download_data.py` descarga el zip desde la URL configurada, calcula el SHA-256 de los bytes recibidos, comprueba que ninguna ruta del zip salga de la carpeta de destino y lo extrae en `data/raw/ml-latest-small/`. Los archivos de `data/raw/` no se editan ni se suben a Git; se vuelven a obtener con el script. `uv run python scripts/audit_data.py` carga los datos mediante `load_movielens`, que valida las columnas requeridas, que cada valoración tenga una película en el catálogo y que los ratings estén entre 0,5 y 5,0.

## Población observada y exclusiones
| Dato | Valor |
|---|---|
| Valoraciones | 100.836 |
| Usuarios | 610 |
| Películas en el catálogo | 9.742 |
| Películas con al menos una valoración | 9.724 (18 sin ninguna) |
| Rango temporal | 1996-03-29 a 2018-09-24 (UTC) |
| Densidad (valoraciones / usuarios × películas del catálogo) | 0,01697 (1,7 %) |
| Rating medio / mediana / desviación | 3,50 / 3,5 / 1,04 |

Según el README oficial, los usuarios se seleccionaron al azar y cada uno había valorado al menos 20 películas; los usuarios con menos valoraciones no están. Los identificadores son anónimos y el conjunto no incluye demografía. El universo observado es este subconjunto de usuarios y películas, no toda la población ni todo el catálogo.

## Calidad, sesgos y usos prohibidos
**Calidad.** El esquema se valida al cargar. La densidad es muy baja: la mayoría de las combinaciones usuario–película no tiene valoración, y eso no significa rechazo.

**Sesgos y límites.**
- **Autoselección:** solo se observan valoraciones de películas que las personas decidieron ver y valorar.
- **Popularidad:** unas pocas películas acumulan muchas valoraciones y la mayoría muy pocas, lo que favorece a las populares.
- **Cold start:** los usuarios y películas sin historial no tienen señal colaborativa.
- **Antigüedad:** los datos terminan en septiembre de 2018 y no reflejan el catálogo ni los gustos actuales.
- **Sin demografía:** no pueden afirmarse resultados por grupos poblacionales.
- **Conjunto de desarrollo:** puede cambiar; el hash permite saber qué bytes se usaron.

**Usos prohibidos.** Uso comercial sin permiso de GroupLens; presentar el trabajo como avalado por GroupLens o la Universidad de Minnesota; identificar o perfilar a personas; extraer conclusiones sobre grupos demográficos; usar este conjunto como referencia para resultados científicos compartidos.
