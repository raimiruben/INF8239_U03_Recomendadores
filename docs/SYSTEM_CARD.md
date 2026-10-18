# System Card · Recomendador

Sistema académico de INF-8239 (Unidad 03). No está desplegado ni se usa con personas reales.

## Usuarios y propósito
- **Quién lo usa:** estudiantes y docente de INF-8239, para comparar métodos de recomendación.
- **Para qué:** ofrecer listas de películas de apoyo a la exploración. Una lista no es una verdad sobre el gusto de nadie.
- **Fuera de alcance:** decidir sobre personas, perfilar o identificar usuarios, uso comercial (la licencia de GroupLens lo exige así) y cualquier conclusión sobre grupos demográficos.

## Catálogo y candidatos
- Catálogo: 9.742 películas de MovieLens Latest Small (9.724 con al menos una valoración).
- Popularidad: ordena por número de valoraciones y luego por media, sobre el entrenamiento, sin las películas ya vistas.
- Contenido: puntúa todas las películas del modelo no vistas.
- Colaborativo: toma las 100 películas no vistas con mayor puntuación y entrega las 10 primeras.
- Híbrido: reordena esas mismas 100 candidatas y entrega las 10 primeras.

## Señales utilizadas
- Valoraciones explícitas de 0,5 a 5,0 (100.836, de 610 usuarios).
- Géneros de cada película (TF-IDF).
- La marca de tiempo solo define el corte entre entrenamiento y prueba.
- No se usan etiquetas, enlaces ni datos demográficos (el conjunto no los incluye).

## Modelos y fallback
- **Contenido:** TF-IDF sobre géneros y similitud coseno. El perfil del usuario es el promedio de los géneros de lo que valoró, ponderado por max(valoración − 2,5; 0,1).
- **Factorización matricial:** descenso de gradiente sin sesgos de usuario ni de película; 20 factores, 12 épocas, tasa de aprendizaje 0,01 y regularización 0,05 (valores del proyecto); semillas 42, 7 y 123.
- **Híbrido:** α × colaborativo + (1 − α) × contenido, con ambas puntuaciones normalizadas entre 0 y 1 dentro de las 100 candidatas de cada usuario. Se probó α = 0,25 y α = 0,75.
- **Respaldo:** si el usuario no tiene historial, se muestra la lista de popularidad, igual para todos.

## Métricas offline
Corte temporal leave-one-out: la última valoración de cada usuario se reserva para prueba. De 610 usuarios, 587 son evaluables (23 quedan fuera porque su película reservada no tiene valoraciones de entrenamiento).

| Método | HitRate@10 | Con corte estricto | Cobertura | Costo (s) |
|---|---|---|---|---|
| Azar esperado | 0,0010 | n/d | n/d | n/d |
| Popularidad | 0,0426 | 0,0384 | 0,012 | 0,007 |
| Contenido | 0,0017 | 0,0020 | 0,078 | 4,2 |
| Colaborativo | 0,0352 ± 0,0055 | 0,0357 | 0,070 | 41,8 |
| Híbrido α = 0,25 | 0,0267 ± 0,0052 | 0,0263 | 0,102 | 41,8 |
| Híbrido α = 0,75 | 0,0352 ± 0,0055 | 0,0343 | 0,072 | 41,8 |

- RMSE de la factorización: 1,026 (±0,0003), frente a 1,116 (media global) y 1,050 (media por película).
- Con 587 usuarios y un acierto cercano a 0,04, el error típico es de unos 0,008. Popularidad, colaborativo e híbrido 0,75 no se distinguen en acierto.
- La columna "con corte estricto" excluye a los 94 usuarios cuya valoración reservada tiene la misma fecha y hora que su última valoración de entrenamiento.
- Costo: tiempo de entrenamiento más inferencia sobre los usuarios evaluables, en una sola ejecución; varía entre ejecuciones y no sirve para comparaciones finas.
- Pareto (acierto, cobertura, costo): sin dominar quedan popularidad, contenido (solo por cobertura), híbrido 0,25 e híbrido 0,75. El colaborativo puro lo domina el híbrido 0,75 por una diferencia mínima.

## Cold start, cobertura y diversidad
- **Usuario nuevo:** recibe la lista de popularidad, igual para todos. Funciona, pero no personaliza. Ejemplo: Forrest Gump, Shawshank Redemption, Pulp Fiction, Matrix, Silence of the Lambs.
- **Historial mínimo (3 valoraciones simuladas):** el contenido da una lista de películas poco conocidas con puntuaciones empatadas; la señal es débil.
- **Película nueva:** la factorización no puede evaluarla ni recomendarla sin valoraciones; el contenido sí, por sus géneros.
- **Cobertura:** la popularidad recomienda el 1,2 % del catálogo; el híbrido 0,75, el 7,2 %; el híbrido 0,25, el 10,2 %. Más peso al contenido da más variedad y menos acierto.
- **Perfiles ejemplo (una película reservada por usuario, ningún método la acertó):** historial amplio (usuario 414, 2.697 valoraciones) y corto (usuario 53, 19 valoraciones). Son ilustraciones, no evidencia de rendimiento.

## Riesgos y monitoreo
| Riesgo | Evidencia | Mitigación y monitoreo propuesto |
|---|---|---|
| Sesgo de popularidad | Popularidad iguala o supera a los métodos personalizados en acierto y cubre el 1,2 % del catálogo | Vigilar la cobertura y la parte del Top-10 que viene de las más populares |
| Sobre-especialización del contenido | Listas de películas de un solo género, con empates en 1,0 y orden arbitrario | No usar el contenido solo; desempatar con otra señal |
| Evaluación ruidosa | Una película reservada por usuario; error típico de unos 0,008 | Repetir con más películas reservadas por usuario antes de afirmar mejoras |
| Corte temporal imperfecto | 94 de 610 usuarios con empate de fecha y hora | Declararlo; reportar también el corte estricto |
| Datos antiguos y sin demografía | Datos de 2018; no hay variables de grupo | No concluir nada sobre grupos; reevaluar con datos actuales |
| Uso fuera de alcance | La lista puede leerse como verdad sobre el gusto | Aviso visible en la aplicación; prohibir perfilado |

Monitoreo si se usara de forma real: recalcular HitRate@10, cobertura y RMSE con datos nuevos cada cierto tiempo; los umbrales de alerta están por definir (propuesta pendiente de aprobación del responsable).
