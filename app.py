import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Test de Catalogo de Productos.csv", layout="wide")
st.title("📦 Diagnóstico de carga: Catalogo de Productos.csv desde mapa_archivos.csv")

# ID FIJO del nuevo mapa_archivos.csv actualizado
MAPA_ID = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"

def es_html(texto):
    return "<html" in texto.lower() or "<!doctype" in texto.lower()

def leer_csv_drive(file_id, nombre):
    st.write(f"🔄 Cargando CSV: {nombre} (ID: {file_id})")
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    if es_html(response.text):
        st.error(f"❌ El archivo {nombre} no está accesible. Puede que no sea público.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", on_bad_lines="skip", engine="python")
        st.success(f"✅ {nombre} cargado correctamente.")
        st.write(f"📌 Columnas de {nombre}:")
        st.write(df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"❌ Error leyendo {nombre}: {e}")
        return pd.DataFrame()

def cargar_mapa():
    url = f"https://drive.google.com/uc?id={MAPA_ID}&export=download"
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip()
    return df

# Cargar mapa_archivos.csv
mapa = cargar_mapa()

# Buscar ID del archivo "Catalogo de Productos.csv"
fila = mapa[mapa["nombre_archivo"] == "Catalogo de Productos.csv"]
if not fila.empty:
    id_catalogo = fila.iloc[0]["id_archivo"]
    df_catalogo = leer_csv_drive(id_catalogo, "Catalogo de Productos.csv")
else:
    st.error("❌ No se encontró 'Catalogo de Productos.csv' en mapa_archivos.csv")
