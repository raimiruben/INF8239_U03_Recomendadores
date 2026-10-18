# INF-8239 · Unidad 03 · Sistemas recomendadores

Estudiante: Raimi De Jesús (matrícula hkh25487) · Maestría en Ciencias de Datos e IA, UASD.
Material base: Edwin Ramón José Nolasco, INF-8239 Ciencia de Datos II (UASD).

Proyecto de LAB08 y LAB09. Compara recomendadores por popularidad, por contenido, por factorización matricial y un híbrido sobre MovieLens. Las recomendaciones son listas de apoyo; no representan la preferencia real de nadie.

## Datos y licencia
- Fuente: MovieLens Latest Small (GroupLens, Universidad de Minnesota), `ml-latest-small`, 100.836 valoraciones, 610 usuarios y 9.742 películas.
- **Los datos no se redistribuyen.** `data/raw/` está excluido de Git; el script de descarga los obtiene y registra el SHA-256 del zip.
- Uso académico bajo las condiciones del README oficial de GroupLens: sin sugerir aval de GroupLens ni de la Universidad de Minnesota, citando a Harper y Konstan (2015), DOI 10.1145/2827872.
- Ficha completa en `docs/DATASET_CARD.md`.

## Reproducir
```powershell
uv python install 3.12
uv sync
uv run python scripts/download_data.py
uv run python scripts/audit_data.py
uv run pytest -q
uv run python scripts/lab08_content.py
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75
uv run python scripts/lab09_compare.py
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/E05_recomendador.ipynb
```
Dependencias congeladas en `uv.lock`. Sin `uv`: `pip install -r requirements.txt` y luego `pip install -e .` (el archivo se generó con `uv export --format requirements-txt --no-hashes --no-emit-project`).

## Estructura
- `src/inf8239_u03/`: carga y validación de datos, recomendadores, métricas.
- `scripts/`: descarga, auditoría y laboratorios (`lab08_content.py`, `lab08_queries.py`, `lab09_hybrid.py`, `lab09_compare.py`).
- `tests/`: pruebas automáticas.
- `reports/`: resultados en CSV.
- `docs/`: Dataset Card, System Card e interpretación de LAB08 y LAB09.
- `notebooks/E05_recomendador.ipynb`: cuaderno ejecutado con la evidencia del Ejercicio 05.
- `app/streamlit_app.py`: demostración del recomendador por contenido.

## Resultados de LAB08
Popularidad ponderada (mínimo de votos por percentil 80; `reports/popular_top10.csv`). Primeros tres puestos:

| Película | Valoraciones | Media | Puntuación ponderada |
|---|---|---|---|
| Shawshank Redemption, The (1994) | 317 | 4,429 | 4,395 |
| Godfather, The (1972) | 192 | 4,289 | 4,243 |
| Fight Club (1999) | 218 | 4,273 | 4,233 |

Contenido (TF-IDF sobre géneros y similitud coseno; `reports/content_queries.csv`, cuatro consultas):
- *Toy Story*, *Alien* y *Schindler's List*: los diez resultados empatan en 1,0 porque comparten exactamente los géneros de la consulta, así que su orden dentro del empate no es informativo.
- *Pulp Fiction*: nueve películas con los mismos géneros y una décima con 0,9285.

## Resultados de LAB09
Corte temporal leave-one-out (la última valoración de cada usuario se reserva para prueba), 610 usuarios, 587 evaluables, tres semillas (42, 7, 123), 20 factores y 12 épocas. Fuente: `reports/lab09_summary.csv`.

| Método | HitRate@10 | Cobertura | Costo (s) | No dominado (Pareto) |
|---|---|---|---|---|
| Azar esperado | 0,0010 | n/d | n/d | n/d |
| Popularidad | 0,0426 | 0,012 | 0,007 | sí |
| Contenido | 0,0017 | 0,078 | 4,2 | sí (solo por cobertura) |
| Colaborativo | 0,0352 ± 0,0055 | 0,070 | 41,8 | no |
| Híbrido α = 0,25 | 0,0267 ± 0,0052 | 0,102 | 41,8 | sí |
| Híbrido α = 0,75 | 0,0352 ± 0,0055 | 0,072 | 41,8 | sí |

RMSE de la factorización: 1,026 (±0,0003 entre semillas), frente a 1,116 de la media global y 1,050 de la media por película.

Lectura: popularidad, colaborativo e híbrido 0,75 no se distinguen en acierto con esta muestra (error típico de unos 0,008); el contenido solo no supera al azar de forma útil. Decisión propuesta: híbrido α = 0,75 con respaldo de popularidad para usuarios sin historial, por su mayor cobertura de catálogo a igual acierto. No se demostró una mejora de acierto sobre la popularidad. Detalle en `docs/INTERPRETACION_LAB08_LAB09.md` y `docs/SYSTEM_CARD.md`.

## Límites
- La similitud mide coincidencia de géneros, no gusto, calidad ni época (sobre-especialización).
- La popularidad es idéntica para todos los usuarios y favorece a lo ya popular.
- Para 94 de 610 usuarios la valoración reservada comparte fecha y hora con la última de entrenamiento; con solo los 516 estrictamente posteriores las conclusiones no cambian.
- 23 usuarios no se evalúan porque su película reservada no tiene valoraciones de entrenamiento.
- Una sola película reservada por usuario hace que HitRate@10 sea bajo y ruidoso.
- El conjunto es de 2018, con densidad de 1,7 %, sin demografía; no permite conclusiones por grupos.
- MovieLens Latest Small es un conjunto de desarrollo y GroupLens no lo recomienda como referencia de resultados científicos compartidos.

## Estado
- LAB08 y LAB09: ejecutados y documentados.
- Ejercicio 05: cuaderno ejecutado y `requirements.txt` incluidos; falta el PDF de entrega.

## Uso de IA
Declaración en `docs/AI_USE_DECLARATION.md`.
