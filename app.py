
import streamlit as st
import pandas as pd

# Configuración de la app
st.set_page_config(page_title="Consulta de Existencias - Packsys", layout="wide")
st.image("packsys_logo.png", width=300)
st.title("Consulta de Existencias de Producto")

# URL directa del archivo de existencias
url_existencias = "https://drive.google.com/uc?id=1-HP94DB2jNSqs8lv7XDAeQ3DfoQuggfX"

# Intento seguro para leer el archivo
try:
    df_preview = pd.read_csv(url_existencias, encoding="utf-8-sig", nrows=5)
    st.success("✅ Archivo cargado correctamente. Previsualización:")
    st.dataframe(df_preview)
except Exception as e:
    st.error("❌ Error al cargar el archivo desde Google Drive:")
    st.code(str(e))
