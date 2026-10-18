# Interpretación · LAB08 y LAB09

## LAB08

**Resultado principal.** La popularidad ponderada da un Top-10 igual para todos los usuarios, encabezado por *Shawshank Redemption* (media 4,429; 317 valoraciones; puntuación ponderada 4,395). El recomendador por contenido da una lista distinta para cada película de referencia, basada solo en los géneros.

**Evidencia.** `reports/popular_top10.csv`, `reports/content_recommendations.csv`, `reports/content_queries.csv` (cuatro consultas de géneros distintos), la Dataset Card con el SHA-256 de los datos y las pruebas de `tests/`.

**Qué representa la similitud.** Coincidencia de etiquetas de género, no gusto ni calidad. En *Toy Story*, *Alien* y *Schindler's List* los diez primeros empatan en 1,0, así que su orden no tiene significado. En *Pulp Fiction* solo nueve películas comparten sus géneros exactos.

**Cold start.** Ambos métodos funcionan sin historial del usuario, pero ninguno personaliza. El de contenido también sirve para películas nuevas, porque solo necesita sus géneros.

**Sobre-especialización.** *Alien* recibe solo películas Horror|Sci-Fi, incluidas de serie B. La popularidad favorece a lo ya popular.

**Decisión.** Usar popularidad como respaldo y contenido como señal complementaria; medir con LAB09.

## LAB09

**Resultado en valoraciones.** La factorización predice la valoración con un RMSE de 1,026 (±0,0003 entre tres semillas). La media global da 1,116 y la media por película, 1,050. Mejora a ambas, pero solo un 2,3 % sobre la segunda.

**Resultado en ranking.** Con 587 usuarios evaluables, popularidad (0,0426), colaborativo (0,0352) e híbrido α = 0,75 (0,0352) no se distinguen: el error típico es de unos 0,008, equivalente a unos 25 contra 21 aciertos. El contenido solo (0,0017) está al nivel del azar (0,0010). El híbrido α = 0,25 baja a 0,0267.

**Cobertura del catálogo.** Popularidad recomienda el 1,2 % del catálogo; colaborativo, 7,0 %; híbrido 0,75, 7,2 %; híbrido 0,25, 10,2 %. A más peso del contenido, más variedad y menos acierto.

**Usuario frío.** Un usuario sin historial recibe la lista de popularidad, igual para todos. Con tres valoraciones, el contenido da una lista empatada de películas poco conocidas: la señal es débil. La factorización no puede evaluar películas sin valoraciones.

**Configuración seleccionada y evidencia.** Híbrido α = 0,75 con respaldo de popularidad para usuarios sin historial. Evidencia: `reports/lab09_summary.csv`, `reports/lab09_comparison.csv`, `reports/hybrid_metrics_alpha0.75.json` y `reports/hybrid_metrics_alpha0.25.json`. Se elige porque iguala en acierto a la popularidad dentro del error de medición y recomienda unas seis veces más variedad del catálogo. No se demostró una mejora de acierto sobre la popularidad.

**Costo computacional.** El colaborativo y el híbrido cuestan unos 42 s (entrenamiento más inferencia sobre 587 usuarios); el contenido, 4 s; la popularidad, menos de 0,01 s. Los tiempos varían entre ejecuciones y son orientativos.

**Riesgo principal y mitigación.** La evaluación con una sola película reservada por usuario es ruidosa y puede llevar a afirmar mejoras que no existen. Además, el corte no es estrictamente temporal para 94 de 610 usuarios. Mitigación: reportar el error típico y el corte estricto, no afirmar superioridad sobre la popularidad y repetir con más películas reservadas antes de cualquier uso real.
