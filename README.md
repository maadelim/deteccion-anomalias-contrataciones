# Detección de Anomalías en Contrataciones Públicas del Perú


[![CI — Tests](https://github.com/maadelim/deteccion-anomalias-contrataciones/actions/workflows/ci.yml/badge.svg)](https://github.com/maadelim/deteccion-anomalias-contrataciones/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

Proyecto de ciencia de datos aplicado a la identificación de patrones anómalos en contrataciones públicas registradas en el sistema CONOSCE/OSCE, mediante técnicas de clustering no supervisado.

---

## Descripción

Este proyecto analiza más de **267,000 registros** de adjudicaciones de contrataciones públicas en Perú (2022-2025), con el objetivo de identificar contrataciones cuyo comportamiento se desvía significativamente de lo esperado, ya sea por diferencias extremas entre el monto presupuestado y el monto pagado, o por duraciones de procesos atípicas.

El enfoque no busca afirmar la existencia de fraude o irregularidades, sino **reducir el universo de revisión** para un auditor o perito, señalando los casos estadísticamente más atípicos para su evaluación posterior.

---

## Objetivo

Aplicar algoritmos de clustering (K-means, clustering jerárquico, DBSCAN) sobre datos abiertos de contrataciones públicas para:

- Identificar grupos de contrataciones con comportamiento similar
- Aislar contrataciones con comportamiento anómalo (sobrecostos extremos, procesos atípicamente largos o cortos)
- Generar una lista priorizada de casos para revisión manual

---

## Fuente de datos

Datos abiertos del [Portal de Datos Abiertos del OECE (antes OSCE)](https://www.gob.pe/14272-acceder-al-portal-de-datos-abiertos-del-oece), sistema CONOSCE, correspondientes a adjudicaciones del Sistema Electrónico de Contrataciones del Estado (SEACE), periodo 2022-2025.

Los archivos originales (`.xlsx`) no se incluyen en este repositorio por su tamaño. Para reproducir el proyecto, descargue los archivos de **"Datos de la Adjudicación"** para los años 2022-2025 y colóquelos en `data/raw/` con los nombres:

CONOSCE_ADJUDICACIONES2022_0.xlsx
CONOSCE_ADJUDICACIONES2023_0.xlsx
CONOSCE_ADJUDICACIONES2024_0.xlsx
CONOSCE_ADJUDICACIONES2025_0.xlsx


---

## Metodología

### 1. Carga y unificación de datos

Se cargaron y concatenaron los 4 archivos anuales, obteniendo un conjunto de datos de **267,772 registros y 25 columnas**. El módulo `data_loader.py` valida la existencia de cada archivo antes de cargarlo y emite advertencias si alguno está ausente, evitando errores silenciosos.

### 2. Limpieza de datos

Se eliminaron registros con valores nulos en columnas críticas (montos, fechas, tipo de proveedor), resultando en **267,698 registros**. Adicionalmente, se eliminaron registros con `dias_proceso` negativos, correspondientes a errores de registro de fechas.

### 3. Feature engineering

Se crearon las siguientes variables:

- `diferencia_monto`: diferencia entre el monto adjudicado y el monto referencial (en soles)
- `diferencia_pct`: diferencia porcentual entre ambos montos
- `diferencia_pct_cap`: versión acotada entre -100% y +500% para controlar valores extremos (justificación: montos referenciales casi nulos generaban porcentajes del orden de 10^10%, distorsionando el clustering; el rango cubre desde "se pagó nada" hasta "se pagó 6x lo presupuestado")
- `dias_proceso`: días transcurridos entre la fecha de convocatoria y la fecha de buena pro

Se identificaron y separaron **587 registros** con monto referencial igual a cero, tratados como un grupo especial de posibles errores de registro.

### 4. Tratamiento de outliers

La variable `diferencia_pct` presentaba valores extremos (hasta el orden de 10^10%) debido a montos referenciales casi nulos. Se aplicó capping entre -100% y +500%, afectando solo el **0.02%** de los registros.

### 5. Escalado

Las variables numéricas se escalaron con `StandardScaler` para que tuvieran media 0 y desviación estándar 1, condición necesaria para que el clustering no esté dominado por variables de mayor magnitud (como los montos en soles).

### 6. Clustering jerárquico (exploratorio)

Sobre una muestra de 2,000 registros, se generó un dendrograma con linkage de Ward para explorar visualmente la estructura de los datos y orientar la elección del número de clusters.

### 7. Selección de variables: monto vs. comportamiento

Un primer modelo K-means (k=4) utilizando variables de monto fue dominado por la magnitud de los contratos, agrupando principalmente por tamaño y no por comportamiento anómalo.

Se optó por un segundo modelo enfocado en **variables de comportamiento**, independientes del tamaño del contrato:

- `diferencia_pct_cap`
- `dias_proceso`

### 8. Determinación del número de clusters

Se aplicó el método del codo sobre las variables de comportamiento, evaluando k entre 1 y 10. Se identificó un codo entre k=4 y k=5, seleccionando **k=4**.

### 9. Clustering final (K-means, k=4)

Se aplicó K-means sobre las 267,111 contrataciones con monto referencial distinto de cero.

### Validación cuantitativa del modelo

La elección de k=4 fue validada con tres métricas internas calculadas sobre los 267,111 registros:

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Silhouette Score | **0.5601** | Bueno (↑ mejor, máx=1). Clusters bien separados entre sí. |
| Davies-Bouldin Index | **0.6871** | Muy bueno (↓ mejor, mín=0). Alta cohesión interna. |
| Calinski-Harabasz Score | **138,159** | Excelente (↑ mejor). Refleja la fuerte separación del Cluster 3. |

Los tres indicadores confirman que k=4 es una partición sólida para estos datos. El valor elevado de Calinski-Harabasz se explica por la separación extrema del Cluster 3 (sobrecosto del +369.8%) respecto al resto del dataset.

---

## Resultados

El modelo identificó 4 grupos de comportamiento:

| Cluster | Registros | % | diferencia_pct_cap (media) | dias_proceso (media) | Interpretación |
|---------|-----------|------|---------------------------|----------------------|----------------|
| 0 | 217,671 | 81.5% | -2.4% | 24.5 | Comportamiento normal |
| 1 | 44,765 | 16.8% | -33.5% | 37.8 | Pago significativamente menor al presupuestado |
| 2 | 4,587 | 1.7% | -26.0% | 330.4 | Procesos de duración atípicamente larga |
| 3 | 168 | 0.06% | +369.8% | 51.3 | Sobrecosto extremo |

### Casos prioritarios (Cluster 3)

De los 168 registros del Cluster 3, se identificaron **78 casos** con monto referencial superior a 1,000 soles (excluyendo posibles errores de registro), exportados en `results/casos_sospechosos.csv`.

Estos casos presentan sobrecostos de entre 5 y 17 veces el monto presupuestado, en entidades como PETROPERÚ S.A., universidades nacionales y gobiernos regionales.

---

## Comparación con DBSCAN

Como complemento al modelo K-means, se aplicó **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise), un algoritmo basado en conectividad por densidad que identifica automáticamente los puntos que no pertenecen a ninguna región densa, clasificándolos como "ruido".

### Consideraciones de escalabilidad

DBSCAN requiere calcular distancias entre todos los pares de puntos, lo que resultó en un error de memoria al aplicarlo sobre el dataset completo (267,111 registros). Por esta razón, se aplicó sobre una **muestra aleatoria de 10,000 registros** (semilla fija para reproducibilidad). El valor óptimo de `eps` puede estimarse con la función `calcular_eps_optimo()` incluida en `src/clustering.py`, que genera la curva de distancia al k-ésimo vecino.

### Resultados (muestra de 10,000 registros)

| Cluster DBSCAN | Registros | diferencia_pct_cap (media) | dias_proceso (media) | Interpretación |
|----------------|-----------|---------------------------|----------------------|----------------|
| 0 | 9,844 | +7.7% | 28.4 | Comportamiento normal (zona densa) |
| -1 (ruido) | 129 | +19.4% | 269.8 | Procesos de duración atípicamente larga |
| 1 | 27 | -97.0% | 548.8 | Procesos extremadamente largos con pago muy por debajo de lo presupuestado |

### K-means vs. DBSCAN: hallazgos complementarios

Ambos algoritmos identifican anomalías, pero con sensibilidades distintas:

- **K-means (k=4)** fue más sensible a anomalías de magnitud, destacando un grupo de 168 contrataciones (0.06%) con sobrecostos extremos (+369.8% en promedio).
- **DBSCAN** fue más sensible a anomalías de densidad/tiempo, destacando grupos de contrataciones con duraciones de proceso muy por encima de lo habitual (270 a 548 días frente a un promedio general de ~32 días).

Esto sugiere que ambos enfoques son complementarios: K-means resulta útil para priorizar casos por **sobrecosto**, mientras que DBSCAN resulta útil para priorizar casos por **duración anómala del proceso**.

---

## Análisis adicional: Contrataciones Directas

Como extensión del análisis, se incorporó el dataset de Contrataciones Directas (procesos adjudicados sin concurso competitivo, bajo causales como situación de emergencia, proveedor único o desabastecimiento inminente), para evaluar si los casos de sobrecosto extremo (Cluster 3) estaban asociados a este tipo de procesos.

Se unificaron los archivos de Contrataciones Directas (2022-2025), totalizando 20,928 registros. Mediante la columna `codigoconvocatoria`, se creó una variable binaria `es_contratacion_directa`, identificando 20,575 registros (7.7% del total).

Las causales más frecuentes fueron: situación de emergencia (34.5%), proveedor único (19.9%), desabastecimiento inminente (16.9%) y arrendamiento de bienes inmuebles (16.5%).

### Resultado

| Cluster | % Contrataciones Directas |
|---------|--------------------------|
| 0 (Normal) | 9.31% |
| 1 (Pago menor al presupuestado) | 0.65% |
| 2 (Procesos largos) | 0.31% |
| 3 (Sobrecosto extremo) | 1.79% |

**La hipótesis no se confirmó.** El Cluster 0 (comportamiento normal) presenta la mayor proporción de contrataciones directas (9.31%), mientras que el Cluster 3 (sobrecosto extremo) presenta una proporción menor (1.79%). Una posible explicación es que las contrataciones directas suelen tener montos pactados desde el inicio, con poco margen de variación posterior. Los sobrecostos extremos parecen estar más asociados a procesos competitivos donde el monto referencial se calculó incorrectamente.

---

## Análisis adicional: Concentración de proveedores

Se analizó la distribución de adjudicaciones por proveedor (`ruc_proveedor`) sobre 104,551 proveedores distintos:

| Estadístico | Valor |
|-------------|-------|
| Promedio de ítems ganados | 2.55 |
| Mediana (P50) | 1 |
| Percentil 75 | 1 |
| Máximo | 2,191 |

El proveedor con más adjudicaciones fue **Grupo Santa Fe S.A.C.** (RUC 20511037001): 2,191 ítems adjudicados, 295 entidades públicas distintas como clientes, monto total de S/. 439,933,852.92 y 100% en la categoría "Bien". Las características del caso son consistentes con el perfil de un proveedor establecido a nivel nacional, más que con un patrón de favoritismo.

---

## Visualizaciones

![Distribución de clusters](results/resumen_clusters.png)

El notebook `01_exploracion.ipynb` incluye además:

- Dendrograma jerárquico (muestra de 2,000 registros)
- Gráfico de dispersión: clusters por monto referencial vs. diferencia porcentual
- Gráfico de dispersión: clusters de comportamiento (días de proceso vs. diferencia porcentual)

---

## Tecnologías utilizadas

- Python 3.11
- pandas, numpy
- scikit-learn (KMeans, DBSCAN, StandardScaler, NearestNeighbors)
- scipy (clustering jerárquico)
- matplotlib, seaborn
- Jupyter Notebook

---

## Estructura del repositorio

```
deteccion-anomalias-contrataciones/
├── data/
│   ├── raw/                    # Archivos originales (no incluidos, ver instrucciones)
│   └── processed/
├── notebooks/
│   ├── 01_exploracion.ipynb    # Análisis exploratorio completo, paso a paso
│   └── 02_pipeline.ipynb       # Pipeline limpio y reproducible usando src/
├── src/
│   ├── init.py             # Hace src/ importable como paquete Python
│   ├── config.py               # Constantes y parámetros centralizados
│   ├── logging_config.py       # Configuración de logging uniforme
│   ├── data_loader.py          # Carga y unificación de los datasets anuales
│   ├── preprocessing.py        # Limpieza de datos y feature engineering
│   └── clustering.py           # K-Means, DBSCAN y utilidad calcular_eps_optimo()
├── results/
│   ├── casos_sospechosos.csv   # 78 casos de sobrecosto extremo priorizados
│   └── resumen_clusters.png    # Visualización de clusters K-Means y DBSCAN
├── requirements.txt      # Dependencias mínimas del proyecto
├── requirements-dev.txt  # Dependencias de desarrollo (JupyterLab, etc.)
├── Makefile              # Comandos para reproducir el proyecto (make install, make test, make run)
└── README.md

 
 ---

## Sobre los dos notebooks

- **`01_exploracion.ipynb`**: contiene el proceso completo de análisis exploratorio, incluyendo la justificación de cada decisión (tratamiento de outliers, elección de variables, comparación de modelos). Es el notebook recomendado para entender el razonamiento detrás del proyecto.
- **`02_pipeline.ipynb`**: ejecuta el pipeline completo (carga → limpieza → clustering → visualización → exportación) en pocas líneas, usando los módulos de `src/`. Facilita la reproducción e integración en otros flujos de trabajo.

---

## Sobre los módulos de `src/`

| Módulo | Función principal | Descripción |
|--------|------------------|-------------|
| `config.py` | — | Centraliza nombres de columnas, rutas y parámetros de los modelos. Modifica aquí para ajustar el comportamiento sin tocar el código. |
| `logging_config.py` | `configurar_logging()` | Activa el sistema de logging del proyecto. Llamar al inicio de cada notebook. |
| `data_loader.py` | `cargar_adjudicaciones()` | Carga los 4 archivos anuales con validación de existencia y logging de progreso. |
| `preprocessing.py` | `limpiar_y_preparar()` | Limpieza, feature engineering y separación de casos con monto referencial = 0. Retorna `(df_model, df_monto_cero)`. |
| `clustering.py` | `aplicar_kmeans()`, `aplicar_dbscan_muestra()`, `calcular_eps_optimo()` | K-Means sobre el dataset completo; DBSCAN sobre muestra; utilidad para determinar el eps óptimo por la curva del k-ésimo vecino. |

Esta separación permite que el pipeline sea fácilmente extensible: incorporar un nuevo dataset solo requiere modificar `data_loader.py`, sin tocar la lógica de limpieza o clustering.

---


## Cómo reproducir el proyecto

### Opción 1 — Con Make (recomendado)

```bash
git clone https://github.com/maadelim/deteccion-anomalias-contrataciones.git
cd deteccion-anomalias-contrataciones
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
make install
make test
make run
```

### Opción 2 — Manual

```bash
git clone https://github.com/maadelim/deteccion-anomalias-contrataciones.git
cd deteccion-anomalias-contrataciones
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
jupyter notebook notebooks/01_exploracion.ipynb
```

# (Opcional) Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Colocar los archivos de datos en data/raw/ (ver sección "Fuente de datos")

# Ejecutar el notebook exploratorio
jupyter notebook notebooks/01_exploracion.ipynb

# O ejecutar el pipeline limpio
jupyter notebook notebooks/02_pipeline.ipynb
```

---

## Limitaciones y consideraciones

- El clustering identifica desviaciones estadísticas, no determina por sí mismo la existencia de irregularidades; los resultados requieren validación por un experto en la materia (peritaje contable).
- Algunos registros con montos referenciales extremadamente bajos (cercanos a cero) generan porcentajes de diferencia poco interpretables y se tratan como un grupo separado de posible error de registro, no como anomalías de comportamiento.
- El periodo analizado (2022-2025) no incluye el contexto de contrataciones de emergencia sanitaria (2020-2021), que tienen reglas y patrones distintos.
- DBSCAN se aplica sobre una muestra de 10,000 registros por limitaciones de memoria. El valor de `eps` puede ajustarse usando `calcular_eps_optimo()` en `src/clustering.py`.

---

## Próximos pasos

- ~~Evaluar Isolation Forest~~ ✅ **Implementado** en `src/clustering.py` como `aplicar_isolation_forest()`.
- Análisis de sensibilidad del número de clusters ✅ Evaluado k=2..6 con Silhouette Score (ver `results/sensibilidad_k.png`).
- Comparación cuantitativa de los 3 modelos ✅ Tabla comparativa K-Means / DBSCAN / Isolation Forest en `01_exploracion.ipynb`.
- Persistencia del modelo ✅ Scaler y KMeans serializados con joblib en `results/` para inferencia sin reentrenar.
- Incorporar variables categóricas adicionales (tipo de entidad, tipo de proceso de selección) mediante codificación One-Hot o Target Encoding.
- Explorar **HDBSCAN** (disponible en scikit-learn ≥ 1.3) para escalar el análisis de densidad al dataset completo sin muestreo.
- Incorporar recurrencia de proveedores y tiempos de aprobación como variables para detectar irregularidades en contrataciones directas.

---

## Conclusiones generales

Este proyecto aplicó técnicas de clustering no supervisado (K-means, clustering jerárquico y DBSCAN) sobre 267,111 registros de adjudicaciones públicas en Perú (2022-2025).

**Principales hallazgos:**

- El comportamiento normal domina el dataset: el 81.5% de las contrataciones presentan diferencias pequeñas y tiempos de proceso cercanos al promedio (~25 días).
- Existen patrones de anomalía de distinta naturaleza: 168 contrataciones (0.06%) con sobrecostos extremos (+369.8% promedio), detectadas por K-means; y grupos con duraciones de proceso de 270 a 548 días, detectados por DBSCAN. Ambos tipos de anomalía no coinciden necesariamente en los mismos registros.
- Las hipótesis exploradas no siempre se confirmaron, y eso es informativo: los sobrecostos extremos están más asociados a procesos competitivos que a contrataciones directas.
- La concentración de proveedores es alta pero no necesariamente irregular; el análisis de contexto es indispensable antes de calificar un patrón como anómalo.

El clustering permite reducir el universo de revisión de 267,111 registros a un conjunto acotado y priorizado sobre el cual un perito contable puede enfocar su análisis.

---

## Aprendizajes técnicos

- La elección de variables determina qué tipo de anomalía detecta el modelo: variables de monto agrupan por tamaño; variables de comportamiento detectan anomalías independientes de la escala.
- Algoritmos distintos (K-means y DBSCAN) son sensibles a distintos tipos de anomalía; su uso combinado ofrece una visión más completa.
- DBSCAN no escala a cientos de miles de registros sin muestreo; el eps óptimo debe determinarse empíricamente con la curva del k-ésimo vecino.
- Refutar una hipótesis con datos adicionales es tan valioso como confirmarla.

---

## Autora

Hecho por Madelim Mallma Moreno
