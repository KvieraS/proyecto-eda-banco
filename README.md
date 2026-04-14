# Proyecto EDA - Campañas de marketing bancario

## Descripción
Este proyecto consiste en la realización de un análisis exploratorio de datos (EDA) utilizando Python y Pandas sobre distintos conjuntos de datos relacionados con campañas de marketing directo de una institución bancaria portuguesa.  

El objetivo principal ha sido limpiar, transformar, unir y analizar los datos para detectar patrones relevantes en el comportamiento de los clientes y en la suscripción de depósitos a plazo.

---

## Objetivos del proyecto
- Realizar la transformación y limpieza de los datos.
- Llevar a cabo un análisis descriptivo de las variables principales.
- Generar visualizaciones que ayuden a interpretar los datos.
- Elaborar un informe explicativo con los principales hallazgos.
- Aplicar buenas prácticas de programación en Python y uso eficiente de Pandas.

---

## Herramientas utilizadas
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Visual Studio Code

---

## Conjuntos de datos utilizados

### 1. `bank-additional.csv`
Contiene información sobre campañas de marketing bancario realizadas mediante llamadas telefónicas. Incluye variables como:
- edad
- profesión
- estado civil
- nivel educativo
- préstamos
- duración de la llamada
- número de contactos realizados
- resultado de campañas anteriores
- variables económicas
- variable objetivo `y`, que indica si el cliente suscribió o no el producto

### 2. `customer-details.xlsx`
Archivo Excel con 3 hojas (`2012`, `2013`, `2014`) que contiene información adicional de los clientes:
- ingresos anuales
- número de niños y adolescentes en el hogar
- fecha de alta como cliente
- visitas mensuales a la web
- identificador del cliente

---

## Estructura del repositorio

```bash
.
├── README.md
├── data
│   ├── raw
│   │   ├── bank-additional.csv
│   │   └── customer-details.xlsx
│   └── processed
│       ├── customers_unified.csv
│       └── bank_customers_clean.csv
├── figures
│   ├── 01_distribucion_suscripcion.png
│   ├── 02_distribucion_edad.png
│   ├── 03_suscripcion_por_trabajo.png
│   ├── 04_duracion_vs_suscripcion.png
│   ├── 05_income_vs_web_visits.png
│   └── 06_heatmap_correlacion.png
└── src
    └── eda_banco.py
```
Proceso seguido
1. Carga de datos

Se cargó el archivo CSV principal y el Excel de clientes.
En el caso del Excel, se unificaron las tres hojas disponibles en un único dataframe para facilitar el análisis posterior.

2. Limpieza y transformación

Durante esta fase se realizaron varias tareas:

Eliminación de columnas auxiliares como Unnamed: 0.
Normalización de nombres de columnas.
Conversión de variables numéricas que venían en formato texto.
Conversión de fechas a formato datetime.
Corrección del formato europeo en columnas numéricas como nr.employed.
Tratamiento de valores nulos:
mediana en variables numéricas como age, euribor3m, cons.price.idx y nr.employed
moda en variables binarias como default, housing y loan
valor "unknown" en variables categóricas como job, marital y education
Creación de nuevas variables:
contact_month
contact_year
previous_contacted
pdays_clean
subscribed
customer_since_year
customer_since_month
total_children
3. Unión de datasets

Se realizó un merge entre ambos conjuntos de datos usando el identificador del cliente (id_), lo que permitió enriquecer el dataset principal con variables demográficas y de comportamiento digital.

4. Análisis descriptivo

Se analizaron distribuciones, medias, medianas, desviaciones, frecuencias y correlaciones entre variables numéricas, además de estudiar la relación entre distintas variables categóricas y la suscripción del producto.

5. Visualización

Se generaron gráficos para facilitar la interpretación de patrones:

distribución de la variable objetivo
distribución de edad
tasa de suscripción por ocupación
duración de llamada según suscripción
relación entre ingresos y visitas web
mapa de correlaciones
Principales hallazgos

A partir del análisis realizado, se obtuvieron las siguientes conclusiones principales:

Distribución de la variable objetivo

La mayoría de los clientes no suscribieron el producto bancario.
El dataset presenta un claro desbalance:

No suscriben: 88,73%
Sí suscriben: 11,27%
Perfiles con mayor tasa de suscripción

Los grupos laborales con mejor tasa de suscripción fueron:

student
retired
unemployed

Esto sugiere que determinados perfiles pueden mostrar mayor predisposición a contratar el depósito a plazo.

Método de contacto

El contacto mediante cellular presentó una tasa de suscripción claramente superior a telephone, lo que indica que el canal de contacto puede influir de forma importante en el éxito de la campaña.

Resultado de campañas previas

El resultado de campañas anteriores mostró una relación muy fuerte con la suscripción actual:

los clientes con resultado previo success tuvieron una tasa de conversión muy superior al resto
los clientes con campañas previas fallidas o inexistentes mostraron menor propensión a suscribir
Duración de la llamada

La variable duration mostró una relación positiva con la suscripción.
Aun así, esta variable debe interpretarse con cautela, ya que la duración se conoce después del contacto, por lo que resulta útil para explicar el comportamiento observado, pero no sería adecuada por sí sola como predictor previo de decisión.

Variables económicas

Variables como emp.var.rate y euribor3m mostraron relación negativa con la suscripción, lo que puede indicar que el contexto económico también influye en la decisión del cliente.

Variables demográficas adicionales

Tras unir los datos del Excel, se incorporaron variables como ingresos, visitas mensuales a la web y composición del hogar. Estas variables enriquecen el análisis y permiten ampliar la visión del cliente, aunque en este caso su relación directa con la suscripción fue más limitada que otras variables ligadas a la campaña.

Decisiones importantes de limpieza

Durante el proceso hubo dos puntos especialmente relevantes:

Tratamiento de pdays

La variable pdays utiliza el valor 999 para indicar ausencia de contacto reciente.
Por este motivo se creó la columna pdays_clean, sustituyendo 999 por valores nulos para evitar interpretaciones incorrectas en el análisis estadístico.

Conversión de nr.employed

Esta variable venía con formato numérico europeo, por lo que fue necesario transformarla correctamente antes de su uso para evitar errores de conversión y pérdida masiva de valores.

Visualizaciones generadas

El proyecto genera y guarda automáticamente los siguientes gráficos en la carpeta figures:

01_distribucion_suscripcion.png
02_distribucion_edad.png
03_suscripcion_por_trabajo.png
04_duracion_vs_suscripcion.png
05_income_vs_web_visits.png
06_heatmap_correlacion.png
Ejecución del proyecto
1. Instalar dependencias
```bash
python -m pip install pandas numpy matplotlib seaborn openpyxl
```
2. Ejecutar el script
```bash
python src/eda_banco.py
```
3. Resultados generados

Al ejecutar el script se generan automáticamente:

los datos transformados en data/processed
las figuras en la carpeta figures
el resumen de calidad de datos y análisis descriptivo en consola
Conclusiones

Este proyecto ha permitido aplicar de forma práctica conceptos clave de Python for Data, especialmente en:

limpieza y transformación de datos
manejo de archivos
uso de Pandas para filtrado, agrupación y agregaciones
visualización de datos
interpretación de resultados

Además, el análisis muestra que variables como el canal de contacto, el historial de campañas previas y la duración de la llamada tienen una relación clara con la suscripción del producto, mientras que la integración de información demográfica complementa el perfil del cliente y aporta contexto adicional al estudio.
