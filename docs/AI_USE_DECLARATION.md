# Declaración de uso de IA

**Herramienta:** Claude (Anthropic), asistente de IA usado en el chat de claude.ai durante LAB08 y LAB09 de la Unidad 03 (proyecto de recomendadores).

**Finalidad:** explicación del código base y de las métricas; revisión del código base frente a lo que exige el manual; corrección de borradores de documentación y de interpretación; escritura de dos scripts y de un cuaderno; diagnóstico de errores.

## Prompts relevantes (resumidos con mis palabras)

1. "Revisa el código base (configuración, carga de datos, recomendadores, pruebas) y la auditoría de los datos."
2. "Redacta la Dataset Card a partir de la auditoría y del README oficial de GroupLens."
3. "Interpreta la salida de popularidad y de contenido, y las pruebas con géneros distintos."
4. "Revisa `lab09\_hybrid.py` y `metrics.py` y dime qué le falta frente a la rúbrica de LAB09 y del Ejercicio 05."
5. "Interpreta los resultados de LAB09 (comparación, semillas, Pareto, perfiles) y propón la decisión."
6. "Corrige el README, la System Card, la interpretación y el cuaderno del Ejercicio 05 a partir de los resultados."

## Fragmentos afectados

**LAB08**

* `docs/DATASET\_CARD.md`: redactada por la IA con las cifras de mi auditoría (`audit\_data.py`) y las condiciones del README oficial de GroupLens, que la IA consultó. El hash lo calculó `download\_data.py`.
* `scripts/lab08\_queries.py`: escrito por la IA (cuatro consultas de contenido con géneros distintos); lo ejecuté yo.
* `app/streamlit\_app.py`: la línea con la fuente de los datos fue propuesta por la IA y la añadí yo.
* `.gitignore`: la IA propuso quitar las reglas que excluían `reports/` (la rúbrica pide `reports` en el repositorio) y añadir `.env`; lo apliqué yo.
* `README.md`: borrador de la IA, ampliado con los resultados de LAB09.

**LAB09**

* `scripts/lab09\_compare.py`: escrito por la IA para comparar popularidad, contenido, colaborativo e híbrido con tres semillas, error de referencia, cobertura, costo, marca de Pareto y perfiles. La IA lo probó solo con módulos sintéticos que imitan el proyecto; la primera ejecución con los datos reales fue la mía.
* `scripts/lab09\_hybrid.py`: corrección de una línea (`np.asarray(...)` en el cálculo del perfil de géneros) propuesta por la IA y aplicada por mí.
* `docs/SYSTEM\_CARD.md` y `docs/INTERPRETACION\_LAB08\_LAB09.md`: borradores de la IA a partir de `reports/lab09\_summary.csv`, `lab09\_profiles.csv` y `lab09\_diagnostics.json`.
* `notebooks/E05\_recomendador.ipynb`: generado por la IA y ejecutado por mí; sus tablas y gráficas salen de los reportes y de los datos.
* `requirements.txt`: generado con `uv export`; las opciones (`--no-hashes --no-emit-project`) las indicó la IA.

## Decisiones que tomé yo

* La decisión final es el **híbrido con α = 0,75 y respaldo de popularidad para usuarios sin historial**. La IA la propuso porque iguala en acierto a la popularidad dentro del error de medición y cubre más catálogo; yo la adopté. Reconozco que **no se demostró una mejora de acierto sobre la popularidad**.
* Ejecuté el entrenamiento de tres semillas y de los dos valores de alpha, y conservé los resultados tal como salieron.

## Verificaciones humanas

* Ejecuté las pruebas del proyecto (7 en verde) y la compilación de los scripts.
* Ejecuté `download\_data.py`, `audit\_data.py`, `lab08\_content.py`, `lab08\_queries.py`, `lab09\_hybrid.py` con α = 0,75 y 0,25, y `lab09\_compare.py` completo.
* Comprobé que la salida del script del curso con la semilla 42 coincide con la de `lab09\_compare.py` (RMSE, HitRate@10 y cobertura).
* Comprobé con una búsqueda que la Dataset Card contiene el hash y no tiene marcadores `REPLACE`.
* Probé la aplicación Streamlit con películas de distintos géneros y ejecuté el cuaderno completo sin errores.

## Errores detectados y correcciones

* **Script del curso:** `lab09\_hybrid.py` falla con las versiones actuales de las librerías (`np.matrix` no es aceptado por scikit-learn). Se corrigió con `np.asarray`.
* **Afirmación incorrecta de la IA:** dijo que `audit\_data.py` "no comprueba nada"; sí valida, a través de `load\_movielens`. Se corrigió.
* **Archivo equivocado:** la primera copia de la Dataset Card tomó un archivo con el mismo nombre de la Unidad 04. Se detectó porque la búsqueda del hash no encontró nada, y se volvió a copiar con otro nombre.
* **Cuaderno:** una versión que la IA entregó tenía un error de sintaxis en una cadena de texto; se descartó y se sustituyó por una versión probada.
* **`requirements.txt`:** la primera versión incluía hashes y `-e .`, lo que impide instalar con `pip`; se regeneró sin ellos.
* **Corte temporal:** en 94 de 610 usuarios la valoración reservada tiene la misma fecha y hora que su última de entrenamiento. Se midió, se reporta y se calcularon las métricas también con el corte estricto; las conclusiones no cambian.
* **Evaluación:** con 587 usuarios y un acierto cercano a 0,04, popularidad, colaborativo e híbrido 0,75 no se distinguen; así quedó escrito en vez de afirmar una mejora.
* **Gráfica del cuaderno:** las etiquetas de dos métodos se superponían y el título se cortaba; se corrigió.
* Los tiempos de entrenamiento varían entre ejecuciones (de unos 23 s a unos 47 s para el mismo entrenamiento), por lo que se usan solo como orden de magnitud.
* La IA no puede ejecutar código con mis datos: todo resultado numérico procede de mis ejecuciones.

**Responsabilidad:** asumo la responsabilidad sobre el contenido entregado.

