# INF-8239 · Unidad 03 · Sistemas recomendadores

Estudiante: Raimi De Jesús (matrícula FG4207) · Maestría en Ciencias de Datos e IA, UASD.
Material base: Edwin Ramón José Nolasco, INF-8239 Ciencia de Datos II (UASD).

Proyecto de LAB08 y LAB09. Compara recomendadores por popularidad, por contenido, por factorización matricial y un híbrido sobre MovieLens. Las recomendaciones son listas de apoyo; no representan la preferencia real de nadie.

## Datos y licencia

* Fuente: MovieLens Latest Small (GroupLens, Universidad de Minnesota), `ml-latest-small`, 100.836 valoraciones, 610 usuarios y 9.742 películas.
* **Los datos no se redistribuyen.** `data/raw/` está excluido de Git; el script de descarga los obtiene y registra el SHA-256 del zip.
* Uso académico bajo las condiciones del README oficial de GroupLens: sin sugerir aval de GroupLens ni de la Universidad de Minnesota, citando a Harper y Konstan (2015), DOI 10.1145/2827872.
* Ficha completa en `docs/DATASET\_CARD.md`.

## Reproducir

```powershell
uv python install 3.12
uv sync
uv run python scripts/download\_data.py
uv run python scripts/audit\_data.py
uv run pytest -q
```

Dependencias congeladas en `uv.lock`; `requirements.txt` se genera con `uv export`.

## Estructura

* `src/inf8239\_u03/`: carga y validación de datos, recomendadores, métricas.
* `scripts/`: descarga, auditoría y laboratorios (`lab08\_content.py`, `lab08\_queries.py`, `lab09\_hybrid.py`).
* `tests/`: pruebas automáticas.
* `reports/`: resultados en CSV.
* `docs/`: Dataset Card y System Card.
* `app/streamlit\_app.py`: demostración del recomendador por contenido.

## Resultados de LAB08

Popularidad ponderada (mínimo de votos por percentil 80; `reports/popular\_top10.csv`). Primeros tres puestos:

|Película|Valoraciones|Media|Puntuación ponderada|
|-|-|-|-|
|Shawshank Redemption, The (1994)|317|4,429|4,395|
|Godfather, The (1972)|192|4,289|4,243|
|Fight Club (1999)|218|4,273|4,233|

Contenido (TF-IDF sobre géneros y similitud coseno; `reports/content\_queries.csv`, cuatro consultas):

* *Toy Story*, *Alien* y *Schindler's List*: los diez resultados empatan en 1,0 porque comparten exactamente los géneros de la consulta, así que su orden dentro del empate no es informativo.
* *Pulp Fiction*: nueve películas con los mismos géneros y una décima con 0,9285.

## Límites

* La similitud mide coincidencia de géneros, no gusto, calidad ni época (sobre-especialización).
* La popularidad es idéntica para todos los usuarios y favorece a lo ya popular.
* El conjunto es de 2018, con densidad de 1,7 %, sin demografía; no permite conclusiones por grupos.
* MovieLens Latest Small es un conjunto de desarrollo y GroupLens no lo recomienda como referencia de resultados científicos compartidos.

## Estado

* LAB08: completo.
* LAB09 (factorización, híbrido, usuarios fríos, tabla de Pareto): pendiente de ejecutar; se añadirá a este README.

## Uso de IA

Declaración en `docs/AI\_USE\_DECLARATION.md`.

