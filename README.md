# Detección de Anomalías en Contrataciones Públicas del Perú

Proyecto de ciencia de datos aplicado a la identificación de patrones anómalos en contrataciones públicas registradas en el sistema CONOSCE/OSCE, mediante técnicas de clustering no supervisado.

## Descripción

Este proyecto analiza más de **267,000 registros** de adjudicaciones de contrataciones públicas en Perú (2022-2025), con el objetivo de identificar contrataciones cuyo comportamiento se desvía significativamente de lo esperado, ya sea por diferencias extremas entre el monto presupuestado y el monto pagado, o por duraciones de proceso atípicas.

El enfoque no busca afirmar la existencia de fraude o irregularidades, sino **reducir el universo de revisión** para un auditor o perito, señalando los casos estadísticamente más atípicos para su evaluación posterior.

## Objetivo

Aplicar algoritmos de clustering (K-means, clustering jerárquico) sobre datos abiertos de contrataciones públicas para:

- Identificar grupos de contrataciones con comportamiento similar
- Aislar contrataciones con comportamiento anómalo (sobrecostos extremos, procesos atípicamente largos o cortos)
- Generar una lista priorizada de casos para revisión manual

## Fuente de datos

Datos abiertos del **Portal de Datos Abiertos del OECE (antes OSCE)**, sistema CONOSCE, correspondientes a adjudicaciones del Sistema Electrónico de Contrataciones del Estado (SEACE), periodo 2022-2025.

> Los archivos originales (.xlsx) no se incluyen en este repositorio por su tamaño. Pueden descargarse desde el portal oficial: https://www.gob.pe/14272-acceder-al-portal-de-datos-abiertos-del-oece

Para reproducir este proyecto, descargar los archivos de "Datos de la Adjudicación" para los años 2022-2025 y colocarlos en `data/raw/` con los nombres:

```
CONOSCE_ADJUDICACIONES2022_0.xlsx
CONOSCE_ADJUDICACIONES2023_0.xlsx
CONOSCE_ADJUDICACIONES2024_0.xlsx
CONOSCE_ADJUDICACIONES2025_0.xlsx
```

## Metodología

### 1. Carga y unificación de datos
Se cargaron y concatenaron los 4 archivos anuales, obteniendo un dataset de 267,772 registros y 25 columnas.

### 2. Limpieza de datos
Se eliminaron registros con valores nulos en columnas críticas (montos, fechas, tipo de proveedor), resultando en 267,698 registros.

### 3. Feature engineering
Se crearon las siguientes variables:

- **diferencia_monto**: diferencia entre el monto adjudicado y el monto referencial (en soles)
- **diferencia_pct**: diferencia porcentual entre ambos montos
- **diferencia_pct_cap**: versión de la anterior, acotada entre -100% y 500% para controlar valores extremos
- **dias_proceso**: días transcurridos entre la fecha de convocatoria y la fecha de buena pro

Se identificaron y separaron 587 registros con monto referencial igual a cero, tratados como un grupo especial de posibles errores de registro.

### 4. Tratamiento de outliers
La variable `diferencia_pct` presentaba valores extremos (hasta el orden de 10^10%) debido a montos referenciales casi nulos. Se aplicó un acotamiento (capping) entre -100% y 500%, afectando solo el 0.02% de los registros.

### 5. Escalado
Las variables numéricas se escalaron con `StandardScaler` para que tuvieran media 0 y desviación estándar 1, condición necesaria para que el clustering no esté dominado por variables de mayor magnitud (como los montos en soles).

### 6. Clustering jerárquico (exploratorio)
Sobre una muestra de 2,000 registros, se generó un dendrograma con linkage de Ward para explorar visualmente la estructura de los datos y orientar la elección del número de clusters.

### 7. Selección de variables: monto vs. comportamiento
Un primer modelo K-means (k=4) utilizando variables de monto fue dominado por la magnitud de los contratos, agrupando principalmente por tamaño y no por comportamiento anómalo.

Se optó por un segundo modelo enfocado en variables de **comportamiento**, independientes del tamaño del contrato:

- `diferencia_pct_cap`
- `dias_proceso`

### 8. Determinación del número de clusters
Se aplicó el método del codo sobre las variables de comportamiento, evaluando k entre 1 y 10. Se identificó un codo entre k=4 y k=5, seleccionando **k=4**.

### 9. Clustering final (K-means, k=4)
Se aplicó K-means sobre las 267,111 contrataciones con monto referencial distinto de cero.

## Resultados

El modelo identificó 4 grupos de comportamiento:

| Cluster | Registros | % | diferencia_pct_cap (media) | dias_proceso (media) | Interpretación |
|---|---|---|---|---|---|
| 0 | 217,671 | 81.5% | -2.4% | 24.5 | Comportamiento normal |
| 1 | 44,765 | 16.8% | -33.5% | 37.8 | Pago significativamente menor al presupuestado |
| 2 | 4,587 | 1.7% | -26.0% | 330.4 | Procesos de duración atípicamente larga |
| 3 | 168 | 0.06% | +369.8% | 51.3 | Sobrecosto extremo |

### Casos prioritarios (Cluster 3)

De los 168 registros del Cluster 3, se identificaron **78 casos** con monto referencial superior a 1,000 soles (excluyendo posibles errores de registro con montos referenciales casi nulos), exportados en `results/casos_sospechosos.csv`.

Estos casos presentan sobrecostos de entre 5 y 17 veces el monto presupuestado, en entidades como PETROPERÚ S.A., universidades nacionales y gobiernos regionales.

# Comparación con DBSCAN

Como complemento al modelo K-means, se aplicó **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise), un algoritmo basado en conectividad por densidad que identifica automáticamente los puntos que no pertenecen a ninguna región densa, clasificándolos como "ruido".

### Consideraciones de escalabilidad

DBSCAN requiere calcular distancias entre todos los pares de puntos, lo que resultó en un error de memoria al aplicarlo sobre el dataset completo (267,111 registros). Por esta razón, se aplicó sobre una **muestra aleatoria de 10,000 registros** (semilla fija para reproducibilidad), siguiendo la misma estrategia utilizada para el dendrograma jerárquico.

### Resultados (muestra de 10,000 registros)

| Cluster DBSCAN | Registros | diferencia_pct_cap (media) | dias_proceso (media) | Interpretación |
|---|---|---|---|---|
| 0 | 9,844 | +7.7% | 28.4 | Comportamiento normal (zona densa) |
| -1 (ruido) | 129 | +19.4% | 269.8 | Procesos de duración atípicamente larga |
| 1 | 27 | -97.0% | 548.8 | Procesos extremadamente largos con pago muy por debajo de lo presupuestado |

### K-means vs. DBSCAN: hallazgos complementarios

Ambos algoritmos identifican anomalías, pero con sensibilidades distintas:

- **K-means (k=4)** fue más sensible a anomalías de **magnitud**, destacando un grupo de 168 contrataciones (0.06%) con sobrecostos extremos (+369.8% en promedio).
- **DBSCAN** fue más sensible a anomalías de **densidad/tiempo**, destacando grupos de contrataciones con duraciones de proceso muy por encima de lo habitual (270 a 548 días frente a un promedio general de ~32 días), independientemente de si el monto se desvió mucho del presupuesto.

Esto sugiere que ambos enfoques son complementarios: K-means resulta útil para priorizar casos por **sobrecosto**, mientras que DBSCAN resulta útil para priorizar casos por **duración anómala del proceso**, una dimensión que el primer modelo no destacaba con la misma claridad.


## Visualizaciones

El notebook incluye:

- Dendrograma jerárquico (muestra de 2,000 registros)
- Gráfico de dispersión: clusters por monto referencial vs. diferencia porcentual
- Gráfico de dispersión: clusters de comportamiento (días de proceso vs. diferencia porcentual)

## Tecnologías utilizadas

- Python 3.11
- pandas, numpy
- scikit-learn (KMeans, StandardScaler)
- scipy (clustering jerárquico)
- matplotlib, seaborn
- Jupyter Notebook

## Estructura del repositorio

```
deteccion-anomalias-contrataciones/
├── data/
│   ├── raw/              # Archivos originales (no incluidos, ver instrucciones de descarga)
│   └── processed/
├── notebooks/
│   └── 01_exploracion.ipynb
├── results/
│   └── casos_sospechosos.csv
├── src/
├── requirements.txt
└── README.md
```

## Cómo reproducir el proyecto

```bash
# Clonar el repositorio
git clone https://github.com/maadelim/deteccion-anomalias-contrataciones.git
cd deteccion-anomalias-contrataciones

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Colocar los archivos de datos en data/raw/ (ver sección "Fuente de datos")

# Ejecutar el notebook
jupyter notebook notebooks/01_exploracion.ipynb
```

## Limitaciones y consideraciones

- El clustering identifica desviaciones estadísticas, no determina por sí mismo la existencia de irregularidades; los resultados requieren validación por un experto en la materia (peritaje contable).
- Algunos registros con montos referenciales extremadamente bajos (cercanos a cero) generan porcentajes de diferencia poco interpretables y deben tratarse como un grupo separado de posible error de registro, no como anomalías de comportamiento.
- El periodo analizado (2022-2025) no incluye el contexto de contrataciones de emergencia sanitaria (2020-2021), que tienen reglas y patrones distintos.

## Próximos pasos

- Incorporar datasets adicionales disponibles (Contrataciones Directas, Consorcios, Convocatorias, Proveedores) para enriquecer el modelo con variables como tipo de proceso, recurrencia de proveedores y consorcios.
- Aplicar clustering jerárquico y DBSCAN sobre el conjunto completo de variables de comportamiento para comparar resultados con K-means.
- Incorporar variables categóricas (tipo de entidad, tipo de proceso de selección) mediante codificación.

## Autora

Made Mallma Moreno
