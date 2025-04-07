
import streamlit as st
import pandas as pd
import requests
import io
import csv

st.set_page_config(page_title="Depuración - mapa_archivos.csv", layout="wide")
st.title("🔧 Depuración de carga de archivo mapa_archivos.csv")

@st.cache_data
def cargar_mapa_archivos(id_mapa):
    url = f"https://drive.google.com/uc?id={id_mapa}&export=download"
    try:
        response = requests.get(url, timeout=10)
        st.write(f"✅ Código de respuesta HTTP: {response.status_code}")
        if response.status_code == 200:
            sample = response.text[:1024]
            try:
                sniff = csv.Sniffer().sniff(sample)
                sep = sniff.delimiter
            except:
                sep = ","
            st.write(f"✅ Separador detectado: '{sep}'")
            return pd.read_csv(io.StringIO(response.text), sep=sep, encoding="utf-8", engine="python", on_bad_lines="skip")
        else:
            st.error("❌ No se pudo descargar el archivo correctamente desde Drive.")
    except requests.exceptions.Timeout:
        st.error("❌ La descarga del archivo desde Google Drive excedió el tiempo de espera.")
    except Exception as e:
        st.error(f"❌ Error inesperado al intentar descargar o procesar el archivo: {e}")
    return pd.DataFrame()

# ID del archivo mapa_archivos.csv
ID_MAPA = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"

# Ejecutar
df = cargar_mapa_archivos(ID_MAPA)

if not df.empty:
    st.subheader("✅ Contenido del archivo:")
    st.dataframe(df)
else:
    st.warning("⚠️ El archivo está vacío o no se pudo cargar.")
