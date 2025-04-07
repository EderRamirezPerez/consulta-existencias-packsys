
import streamlit as st
import pandas as pd
import requests
import io
import csv

st.set_page_config(page_title="Consulta de Existencias Packsys", layout="wide")

st.image("packsys_logo.png", width=200)
st.title("📦 Consulta de Existencias Packsys")

# Función auxiliar: detectar si un archivo es HTML por error
def es_html(texto):
    return "<html" in texto.lower() or "<!doctype" in texto.lower()

# Leer archivo remoto de Drive desde su ID
def leer_csv_drive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    if es_html(response.text):
        st.error(f"❌ El archivo con ID {file_id} no es accesible o no está compartido correctamente.")
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(response.text), encoding="utf-8", on_bad_lines="skip", engine="python")

def leer_excel_drive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    if es_html(response.text):
        st.error(f"❌ El archivo Excel con ID {file_id} no es accesible o no está compartido correctamente.")
        return pd.DataFrame()
    return pd.read_excel(io.BytesIO(response.content), sheet_name=0)

# Cargar mapa_archivos.csv
MAPA_ID = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"

@st.cache_data
def cargar_mapa():
    url = f"https://drive.google.com/uc?id={MAPA_ID}&export=download"
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    return df

mapa = cargar_mapa()

def get_id(nombre_archivo):
    fila = mapa[mapa["nombre_archivo"] == nombre_archivo]
    return fila.iloc[0]["id_archivo"] if not fila.empty else None

# Cargar archivos desde el mapa
id_catalogo = get_id("Catalogo de Productos.csv")
id_existencias = get_id("Existencias Inventario Disponible Localizador.csv")
id_unificacion = get_id("Unificación de claves.xlsx")
id_psd = get_id("PSD multiplicacion de claves.xlsx")

df_catalogo = leer_csv_drive(id_catalogo)
df_existencias = leer_csv_drive(id_existencias)
df_unificacion = leer_excel_drive(id_unificacion)
df_psd_multiplicacion = leer_excel_drive(id_psd)

# Limpieza
df_existencias["Nombre de artículo"] = df_existencias["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
df_unificacion["Nombre de artículo"] = df_unificacion["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
df_psd_multiplicacion["Nombre del articulo"] = df_psd_multiplicacion["Nombre del articulo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
df_catalogo["Nombre de artículo"] = df_catalogo["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)

# Merge y cálculo
df_merged = df_existencias.merge(df_unificacion, on="Nombre de artículo", how="left")
df_merged["Item principal"].fillna(df_merged["Nombre de artículo"], inplace=True)

df_merged = df_merged.merge(df_psd_multiplicacion.rename(columns={"Nombre del articulo": "Nombre de artículo"}), on="Nombre de artículo", how="left")
df_merged["Clave Origen"].fillna(df_merged["Item principal"], inplace=True)
df_merged["Clave Consolidada"] = df_merged["Clave Origen"]

df_merged["Cantidad"] = pd.to_numeric(df_merged["Cantidad"], errors='coerce')
df_merged["Multiplo con base en UM Clave Origen"] = pd.to_numeric(df_merged["Multiplo con base en UM Clave Origen"], errors='coerce').fillna(1)
df_merged["Cantidad Ajustada"] = df_merged["Cantidad"] * df_merged["Multiplo con base en UM Clave Origen"]

df_merged["Organización de inventario"] = df_merged["Organización de inventario"].astype(str).str.strip().str.upper()

almacenes_plataformas = ["MERCADO_LIBRE", "AMAZON"]
almacenes_disponibles = ["PSD_CAT", "LOGISTORAGE_MTY", "DHL_CAT", "CUAUTIPARKII", "WHM_MRD", "DHL_PUEBLA", "DHL_GDL", "LOGISTORAGE_TIJ"]

df_merged["Tipo de Existencia"] = df_merged["Organización de inventario"].apply(lambda x:
    "Existencia en plataformas" if x in almacenes_plataformas else
    "Existencia disponible" if x in almacenes_disponibles else
    f"Otro ({x})"
)

df_merged = df_merged.merge(df_catalogo[["Nombre de artículo", "Artículo - Unidad de medida principal", "PK_PZASTARIMA", "PZAS/PAQUETE"]],
                            on="Nombre de artículo", how="left")

def calcular_conversiones(row):
    cantidad_piezas = row["Cantidad Ajustada"]
    piezas_por_tarima = row["PK_PZASTARIMA"]
    piezas_por_paquete = row["PZAS/PAQUETE"]
    tarimas = cantidad_piezas / piezas_por_tarima if pd.notna(piezas_por_tarima) and piezas_por_tarima > 0 else None
    paquetes = cantidad_piezas / piezas_por_paquete if pd.notna(piezas_por_paquete) and piezas_por_paquete > 0 else None
    return pd.Series([cantidad_piezas, tarimas, paquetes])

df_merged[["Piezas", "Tarimas", "Paquetes"]] = df_merged.apply(calcular_conversiones, axis=1)

df_stock_real = df_merged.groupby(["Clave Consolidada", "Organización de inventario"], as_index=False)                         [["Cantidad Ajustada", "Piezas", "Tarimas", "Paquetes"]].sum()

df_existencias_tipo = df_merged.groupby(["Clave Consolidada", "Tipo de Existencia"], as_index=False)["Cantidad Ajustada"].sum()

# Streamlit Input
clave = st.text_input("🔎 Ingresa una clave de producto:")

if clave:
    producto = clave.strip()
    resultado = df_stock_real[df_stock_real["Clave Consolidada"].astype(str) == producto]
    resultado_tipo = df_existencias_tipo[df_existencias_tipo["Clave Consolidada"].astype(str) == producto]
    df_filtrado = df_merged[df_merged["Clave Consolidada"].astype(str) == producto]

    if not resultado.empty:
        stock_total = resultado["Cantidad Ajustada"].sum()
        st.success(f"✅ Existencias reales de '{producto}': {stock_total:.2f} unidades")

        st.subheader("📦 Desglose por almacén")
        st.dataframe(resultado)

        st.subheader("📊 Existencias por tipo")
        st.dataframe(resultado_tipo)

        for tipo in ["Existencia disponible", "Existencia en plataformas"]:
            df_tipo = df_filtrado[df_filtrado["Tipo de Existencia"] == tipo]
            piezas = df_tipo["Piezas"].sum()
            tarimas = df_tipo["Tarimas"].sum()
            paquetes = df_tipo["Paquetes"].sum()

            st.markdown(f"#### 🔄 Conversión de unidades - {tipo}")
            st.markdown(f"- 🧩 **Piezas**: {piezas:.2f}")
            st.markdown(f"- 🏗️ **Tarimas**: {tarimas:.2f}")
            st.markdown(f"- 📦 **Paquetes**: {paquetes:.2f}")
    else:
        st.warning(f"⚠️ No se encontraron existencias para '{producto}'.")
