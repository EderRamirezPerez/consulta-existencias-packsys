import streamlit as st
import pandas as pd

# Configuración de la app
st.set_page_config(page_title="Consulta de Existencias - Packsys", layout="wide")
st.image("packsys_logo.png", width=300)
st.title("Consulta de Existencias de Producto")

# Enlaces corregidos de Google Drive
urls = {
    "existencias": "https://drive.google.com/uc?id=1-HP94DB2jNSqs8lv7XDAeQ3DfoQuggfX",
    "catalogo": "https://drive.google.com/uc?id=1-Bp-WWIMhWMeEdA5fu-o4ybjc4W7G4d0",
    "psd": "https://drive.google.com/uc?export=download&id=1w2JPGhV-hLZWDFbunX7D4ikmCsWlpzFE",
    "unificacion": "https://drive.google.com/uc?export=download&id=16aIthDrAUr8fFpCdUEXljKRLC3vZ9XLW"
}

@st.cache_data
def cargar_datos():
    df_existencias = pd.read_csv(urls["existencias"], encoding="utf-8-sig")
    df_catalogo = pd.read_csv(urls["catalogo"], encoding="utf-8-sig")
    df_unificacion = pd.read_excel(urls["unificacion"])
    df_psd = pd.read_excel(urls["psd"])
    return df_existencias, df_catalogo, df_unificacion, df_psd

df_existencias, df_catalogo, df_unificacion, df_psd = cargar_datos()
