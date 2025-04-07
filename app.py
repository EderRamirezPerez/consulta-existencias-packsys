import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Diagnóstico de columnas - Packsys", layout="wide")
st.title("🧪 Diagnóstico de columnas en archivos de Drive")

def leer_csv_drive(file_id, nombre):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    try:
        df = pd.read_csv(io.StringIO(response.text), encoding="utf-8", on_bad_lines="skip", engine="python")
        st.success(f"✅ {nombre} cargado correctamente.")
        st.write(f"📌 Columnas de {nombre}:")
        st.write(df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"❌ Error en {nombre}: {e}")
        return pd.DataFrame()

def leer_excel_drive(file_id, nombre):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    try:
        df = pd.read_excel(io.BytesIO(response.content), sheet_name=0)
        st.success(f"✅ {nombre} cargado correctamente.")
        st.write(f"📌 Columnas de {nombre}:")
        st.write(df.columns.tolist())
        return df
    except Exception as e:
        st.error(f"❌ Error en {nombre}: {e}")
        return pd.DataFrame()

# IDs de los archivos en Drive
id_catalogo = "1doNslfQbikbJvKjC1PWGrifmDpXqiKZv"
id_existencias = "1Nj9g8E1CJ7euYtHVp_vcbeI6YRKFE0yg"
id_unificacion = "16aIthDrAUr8fFpCdUEXljKRLC3vZ9XLW"
id_psd = "1w2JPGhV-hLZWDFbunX7D4ikmCsWlpzFE"

# Cargar e inspeccionar columnas
leer_csv_drive(id_catalogo, "Catalogo de Productos.csv")
leer_csv_drive(id_existencias, "Existencias Inventario Disponible Localizador.csv")
leer_excel_drive(id_unificacion, "Unificación de claves.xlsx")
leer_excel_drive(id_psd, "PSD multiplicacion de claves.xlsx")
