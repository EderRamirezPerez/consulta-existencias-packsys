import streamlit as st
import pandas as pd
import requests
import io
import csv

st.set_page_config(page_title="Consulta de Existencias Packsys", layout="wide")

st.title("📦 Consulta de Existencias Packsys")
st.info("🛠 Iniciando carga de archivos desde Google Drive...")

def es_html(texto):
    return "<html" in texto.lower() or "<!doctype" in texto.lower()

def leer_csv_drive(file_id, nombre):
    st.write(f"🔄 Cargando CSV: {nombre} (ID: {file_id})")
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url, timeout=10)
    if es_html(response.text):
        st.error(f"❌ El archivo {nombre} no está compartido correctamente o devolvió HTML.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", on_bad_lines="skip", engine="python")
        st.success(f"✅ {nombre} cargado correctamente.")
        return df
    except Exception as e:
        st.error(f"❌ Error al leer {nombre}: {e}")
        return pd.DataFrame()

def leer_excel_drive(file_id, nombre):
    st.write(f"🔄 Cargando Excel: {nombre} (ID: {file_id})")
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url, timeout=10)
    if es_html(response.text):
        st.error(f"❌ El archivo {nombre} no está compartido correctamente o devolvió HTML.")
        return pd.DataFrame()
    try:
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
        st.success(f"✅ {nombre} cargado correctamente.")
        return df
    except Exception as e:
        st.error(f"❌ Error al leer {nombre}: {e}")
        return pd.DataFrame()

# Leer mapa_archivos.csv
MAPA_ID = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"
def cargar_mapa():
    st.write("📥 Descargando mapa_archivos.csv...")
    url = f"https://drive.google.com/uc?id={MAPA_ID}&export=download"
    try:
        response = requests.get(url)
        df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", engine="python", on_bad_lines="skip")
        df.columns = df.columns.str.strip()
        st.success("✅ Mapa de archivos cargado.")
        return df
    except Exception as e:
        st.error(f"❌ Error cargando mapa_archivos.csv: {e}")
        return pd.DataFrame()

mapa = cargar_mapa()

def get_id(nombre_archivo):
    fila = mapa[mapa["nombre_archivo"] == nombre_archivo]
    if not fila.empty:
        return fila.iloc[0]["id_archivo"]
    else:
        st.warning(f"⚠️ No se encontró ID para '{nombre_archivo}' en el mapa.")
        return None

# 🔁 Dinámicos desde el mapa
id_catalogo = get_id("Catalogo de Productos.csv")
id_existencias = get_id("Existencias Inventario Disponible Localizador.csv")

# 🔒 Fijos (nunca cambian)
id_unificacion = "16aIthDrAUr8fFpCdUEXljKRLC3vZ9XLW"
id_psd = "1w2JPGhV-hLZWDFbunX7D4ikmCsWlpzFE"

# Cargar archivos
df_catalogo = leer_csv_drive(id_catalogo, "Catalogo de Productos")
df_existencias = leer_csv_drive(id_existencias, "Existencias Inventario")
df_unificacion = leer_excel_drive(id_unificacion, "Unificación de claves")
df_psd = leer_excel_drive(id_psd, "PSD multiplicacion de claves")

# Mostrar tablas si se cargaron
if not df_catalogo.empty:
    st.subheader("📄 Catálogo de productos")
    st.dataframe(df_catalogo.head())

if not df_existencias.empty:
    st.subheader("📄 Existencias")
    st.dataframe(df_existencias.head())

if not df_unificacion.empty:
    st.subheader("📄 Unificación de claves")
    st.dataframe(df_unificacion.head())

if not df_psd.empty:
    st.subheader("📄 PSD multiplicación de claves")
    st.dataframe(df_psd.head())
