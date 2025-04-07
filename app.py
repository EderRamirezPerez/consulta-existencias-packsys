
import streamlit as st
import pandas as pd
import requests
import io
import csv

st.set_page_config(page_title="Debug - Ver mapa_archivos", layout="wide")
st.title("🧪 Visualización del archivo mapa_archivos.csv")

@st.cache_data
def cargar_mapa_archivos(id_mapa):
    url = f"https://drive.google.com/uc?id={id_mapa}&export=download"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            sniff = csv.Sniffer().sniff(response.text[:1024])
            sep = sniff.delimiter
        except:
            sep = ","
        return pd.read_csv(io.StringIO(response.text), sep=sep, encoding="utf-8", engine="python", on_bad_lines="skip")
    else:
        st.error("❌ No se pudo descargar el archivo desde Drive.")
        return pd.DataFrame()

# ID del mapa_archivos.csv en Drive
ID_MAPA = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"

# Cargar y mostrar la tabla completa
df = cargar_mapa_archivos(ID_MAPA)

if not df.empty:
    st.subheader("✅ Contenido del archivo cargado:")
    st.dataframe(df)
else:
    st.error("⚠️ El archivo está vacío o no se pudo leer.")
