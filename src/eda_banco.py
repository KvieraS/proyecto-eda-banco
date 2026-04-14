from pathlib import Path
import pandas as pd
import numpy as np
#Para crear graficos
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# CONFIGURACIÓN GENERAL DE FICHEROS Y DIRECTORIOS
# ============================================================

# Configuración de estilo para gráficos
sns.set_theme(style="whitegrid")

# Si el archivo está dentro de /src, esta ruta apunta a la raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
FIGURES_DIR = ROOT_DIR / "figures"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FUNCIONES DE CARGA
# ============================================================

def cargar_bank_data(ruta_csv):
    """Carga los datos del banco desde un archivo CSV.

    Args:
        ruta_csv (Path): Ruta al archivo CSV.

    Returns:
        pd.DataFrame: DataFrame con los datos del banco.
    """
    df = pd.read_csv(ruta_csv)
    return df



def cargar_customer_data(ruta_excel):
    """Carga los datos de los clientes desde un archivo Excel.

    Args:
        ruta_excel (Path): Ruta al archivo Excel.

    Returns:
        pd.DataFrame: DataFrame con los datos de los clientes.
    """
    hojas = pd.ExcelFile(ruta_excel).sheet_names
    dataframes = []

    for hoja in hojas:
        df_hoja = pd.read_excel(ruta_excel, sheet_name=hoja)
        df_hoja["source_sheet"] = hoja
        dataframes.append(df_hoja)

    df_clientes = pd.concat(dataframes, ignore_index=True)
    return df_clientes


# ============================================================
# FUNCIONES DE LIMPIEZA
# ============================================================

def convertir_fechas_espanol(serie):
    """
    Convierte fechas del tipo '2-agosto-2019' a datetime.
    """
    meses = {
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12",
    }

    serie = serie.astype("string").str.strip().str.lower()

    for mes_texto, mes_numero in meses.items():
        serie = serie.str.replace(f"-{mes_texto}-", f"-{mes_numero}-", regex=False)

    return pd.to_datetime(serie, format="%d-%m-%Y", errors="coerce")


def limpiar_bank_data(df):
    """Limpia y transforma el DataFrame del banco para facilitar el análisis posterior.

    Args:
        df (pd.DataFrame): DataFrame con los datos del banco.

    Returns:
        pd.DataFrame: DataFrame limpio y transformado.
    """

    df = df.copy()

    # Elimino columnas auxiliares
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Normalizo nombres de columnas
    df.columns = [col.strip() for col in df.columns]

    # Convierto columnas con coma decimal
    columnas_coma_decimal = ["cons.price.idx", "cons.conf.idx", "euribor3m"]

    for col in columnas_coma_decimal:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype("string")
                .str.strip()
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Conversión especial para nr.employed
    # Ejemplo típico: 5.191,0 -> 5191.0
    if "nr.employed" in df.columns:
        df["nr.employed"] = (
            df["nr.employed"]
            .astype("string")
            .str.strip()
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df["nr.employed"] = pd.to_numeric(df["nr.employed"], errors="coerce")

    # Otras conversiones numéricas
    columnas_numericas = [
        "age", "default", "housing", "loan", "duration", "campaign",
        "pdays", "previous", "emp.var.rate", "latitude", "longitude"
    ]

    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convierto fecha
    if "date" in df.columns:
        df["date"] = convertir_fechas_espanol(df["date"])
        df["contact_month"] = df["date"].dt.month
        df["contact_year"] = df["date"].dt.year

    # Normalizo textos sin convertir NaN en "nan"
    columnas_texto = ["job", "marital", "education", "contact", "poutcome", "y"]
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().str.lower()

    # pdays = 999 suele indicar que no hubo contacto previo reciente
    if "pdays" in df.columns:
        df["previous_contacted"] = np.where(df["pdays"] == 999, 0, 1)
        df["pdays_clean"] = df["pdays"].replace(999, np.nan)

    # Variable binaria más cómoda para análisis
    if "y" in df.columns:
        df["subscribed"] = df["y"].map({"yes": 1, "no": 0})

    # Tratamiento de nulos numéricos
    if "age" in df.columns:
        df["age"] = df["age"].fillna(df["age"].median())

    for col in ["default", "housing", "loan"]:
        if col in df.columns:
            moda = df[col].mode(dropna=True)
            if not moda.empty:
                df[col] = df[col].fillna(moda[0])

    for col in ["euribor3m", "cons.price.idx", "nr.employed"]:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Tratamiento de nulos categóricos
    for col in ["job", "marital", "education"]:
        if col in df.columns:
            df[col] = df[col].fillna("unknown")

    # Paso algunas columnas a entero cuando tiene sentido
    for col in [
        "default", "housing", "loan", "subscribed",
        "contact_month", "contact_year", "previous_contacted"
    ]:
        if col in df.columns:
            df[col] = df[col].astype("Int64")

    return df


def limpiar_customer_data(df):
    """Limpia y transforma el DataFrame de los clientes para facilitar el análisis posterior.

    Args:
        df (pd.DataFrame): DataFrame con los datos de los clientes.

    Returns:
        pd.DataFrame: DataFrame limpio y transformado.
    """
    df = df.copy()

    # Elimino columna auxiliar
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Renombro ID para poder unir con el otro dataset
    if "ID" in df.columns:
        df = df.rename(columns={"ID": "id_"})

    # Convierto fecha de cliente
    if "Dt_Customer" in df.columns:
        df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"], errors="coerce")
        df["customer_since_year"] = df["Dt_Customer"].dt.year
        df["customer_since_month"] = df["Dt_Customer"].dt.month

    # Variables derivadas
    if "Kidhome" in df.columns and "Teenhome" in df.columns:
        df["total_children"] = df["Kidhome"] + df["Teenhome"]

    # Aseguro tipos numéricos
    columnas_numericas = ["Income", "Kidhome", "Teenhome", "NumWebVisitsMonth"]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Por si hubiera nulos en algún momento
    if "Income" in df.columns:
        df["Income"] = df["Income"].fillna(df["Income"].median())

    for col in ["Kidhome", "Teenhome", "NumWebVisitsMonth", "total_children"]:
        if col in df.columns:
            moda = df[col].mode(dropna=True)
            if not moda.empty:
                df[col] = df[col].fillna(moda[0])

    return df


# ============================================================
# MERGE Y CALIDAD DE DATOS
# ============================================================

def unir_datasets(df_bank, df_customer):
    """Une los DataFrames del banco y de los clientes.

    Args:
        df_bank (pd.DataFrame): DataFrame con los datos del banco.
        df_customer (pd.DataFrame): DataFrame con los datos de los clientes.

    Returns:
        pd.DataFrame: DataFrame unido.
    """
    df_merged = df_bank.merge(df_customer, on="id_", how="left")
    return df_merged


def resumen_calidad_datos(df, nombre="DataFrame"):
    """Muestra un resumen de la calidad de los datos.

    Args:
        df (pd.DataFrame): DataFrame con los datos.
        nombre (str, optional): Nombre del DataFrame. Defaults to "DataFrame".
    """
    print("\n" + "=" * 70)
    print(f"RESUMEN DE CALIDAD - {nombre}")
    print("=" * 70)
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nNulos por columna:")
    print(df.isna().sum().sort_values(ascending=False))
    print("\nDuplicados:")
    print(df.duplicated().sum())


# ============================================================
# ANÁLISIS DESCRIPTIVO
# ============================================================

def analisis_descriptivo(df):
    """Realiza un análisis descriptivo de los datos.

    Args:
        df (pd.DataFrame): DataFrame con los datos.
    """
    print("\n" + "=" * 70)
    print("ANÁLISIS DESCRIPTIVO")
    print("=" * 70)

    print("\nResumen estadístico de variables:")
    print(df.describe(include="all"))

    print("\nDistribución de la variable objetivo (y):")
    print(df["y"].value_counts(dropna=False))
    print("\nPorcentaje de suscripción:")
    print((df["y"].value_counts(normalize=True) * 100).round(2))

    print("\nSuscripción por trabajo:")
    print(
        df.groupby("job")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
    )

    print("\nSuscripción por estado civil:")
    print(
        df.groupby("marital")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
    )

    print("\nSuscripción por educación:")
    print(
        df.groupby("education")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
    )

    print("\nSuscripción por tipo de contacto:")
    print(
        df.groupby("contact")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
    )

    print("\nSuscripción por resultado de campaña previa:")
    print(
        df.groupby("poutcome")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .round(3)
    )

    print("\nCorrelación de variables numéricas:")
    columnas_correlacion = [
        "age", "duration", "campaign", "previous", "emp.var.rate",
        "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "Income", "Kidhome", "Teenhome", "NumWebVisitsMonth",
        "total_children", "subscribed"
    ]
    columnas_correlacion = [col for col in columnas_correlacion if col in df.columns]

    print(df[columnas_correlacion].corr(numeric_only=True).round(2))


# ============================================================
# VISUALIZACIONES
# ============================================================

def crear_graficos(df):
    """Crea gráficos para visualizar la información de los clientes.

    Args:
        df (pd.DataFrame): DataFrame con los datos de los clientes.
    """
    # 1. Distribución de la variable objetivo
    plt.figure(figsize=(7, 5))
    ax = sns.countplot(data=df, x="y")
    plt.title("Distribución de suscripción del producto")
    plt.xlabel("Suscripción")
    plt.ylabel("Número de clientes")
    plt.ylim(0, df["y"].value_counts().max() * 1.08)

    total = len(df)
    for barra in ax.patches:
        altura = barra.get_height()
        porcentaje = (altura / total) * 100
        ax.annotate(
            f"{int(altura)}\n({porcentaje:.1f}%)",
            (barra.get_x() + barra.get_width() / 2, altura),
            ha="center",
            va="bottom",
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_distribucion_suscripcion.png")
    plt.close()

    # 2. Histograma de edad
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x="age", bins=30, kde=True)
    plt.title("Distribución de la edad")
    plt.xlabel("Edad")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "02_distribucion_edad.png")
    plt.close()

    # 3. Suscripción media por trabajo
    job_rate = (
        df[df["job"] != "unknown"]
        .groupby("job")["subscribed"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=job_rate, x="subscribed", y="job")
    plt.title("Top 10 ocupaciones por tasa de suscripción")
    plt.xlabel("Tasa de suscripción")
    plt.ylabel("Ocupación")

    for i, valor in enumerate(job_rate["subscribed"]):
        ax.text(valor + 0.003, i, f"{valor:.1%}", va="center")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "03_suscripcion_por_trabajo.png")
    plt.close()

    # 4. Boxplot de duración según suscripción
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="y", y="duration", showfliers=False)
    plt.title("Duración de la llamada según suscripción")
    plt.xlabel("Suscripción")
    plt.ylabel("Duración")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "04_duracion_vs_suscripcion.png")
    plt.close()

    # 5. Distribución de ingresos según suscripción
    if "Income" in df.columns:
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=df, x="y", y="Income", showfliers=False)
        plt.title("Distribución de ingresos según suscripción")
        plt.xlabel("Suscripción")
        plt.ylabel("Income")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "05_distribucion_ingresos_suscripcion.png")
        plt.close()

    # 6. Heatmap de correlación
    columnas_correlacion = [
        "age", "duration", "campaign", "previous", "emp.var.rate",
        "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "Income", "Kidhome", "Teenhome", "NumWebVisitsMonth",
        "total_children", "subscribed"
    ]
    columnas_correlacion = [col for col in columnas_correlacion if col in df.columns]

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        df[columnas_correlacion].corr(numeric_only=True),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5
    )
    plt.title("Mapa de correlación")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "06_heatmap_correlacion.png")
    plt.close()

# ============================================================
# GUARDADO DE RESULTADOS
# ============================================================

def guardar_datos(df_customer, df_final):
    """Guarda los DataFrames procesados en archivos CSV.

    Args:
        df_customer (pd.DataFrame): DataFrame con los datos de los clientes.
        df_final (pd.DataFrame): DataFrame unido con los datos del banco y los clientes.
    """
    df_customer.to_csv(PROCESSED_DIR / "customers_unified.csv", index=False)
    df_final.to_csv(PROCESSED_DIR / "bank_customers_clean.csv", index=False)


# ============================================================
# PROGRAMA PRINCIPAL 
# ============================================================

def main():
    """Iniciar el proceso de EDA para el proyecto del banco. Carga, limpia, une y analiza los datos, además de generar visualizaciones y guardar los resultados.
    """
    print("\nIniciando proyecto EDA...\n")

    # Rutas a los archivos de datos
    bank_path = RAW_DIR / "bank-additional.csv"
    customer_path = RAW_DIR / "customer-details.xlsx"

    # 1. Carga
    df_bank = cargar_bank_data(bank_path)
    df_customer = cargar_customer_data(customer_path)

    # 2. Resumen inicial
    resumen_calidad_datos(df_bank, "Bank raw")
    resumen_calidad_datos(df_customer, "Customer raw")

    # 3. Limpieza
    df_bank_clean = limpiar_bank_data(df_bank)
    df_customer_clean = limpiar_customer_data(df_customer)

    # 4. Merge
    df_final = unir_datasets(df_bank_clean, df_customer_clean)

    # 5. Resumen tras limpieza y unión
    resumen_calidad_datos(df_bank_clean, "Bank clean")
    resumen_calidad_datos(df_customer_clean, "Customer clean")
    resumen_calidad_datos(df_final, "Merged final")

    # 6. Guardado de datos procesados
    guardar_datos(df_customer_clean, df_final)

    # 7. Análisis descriptivo
    analisis_descriptivo(df_final)

    # 8. Visualizaciones
    crear_graficos(df_final)

    print("\nProceso finalizado correctamente.")
    print(f"Datos procesados guardados en: {PROCESSED_DIR}")
    print(f"Gráficos guardados en: {FIGURES_DIR}")


if __name__ == "__main__":
    main()