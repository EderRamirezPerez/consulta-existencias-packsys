
import streamlit as st
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="Consulta de Existencias - Packsys", layout="wide")
st.title("📦 Consulta de Existencias Packsys")

# FUNCIONES

@st.cache_data
def cargar_mapa_archivos(id_mapa):
    url = f"https://drive.google.com/uc?id={id_mapa}&export=download"
    return pd.read_csv(url)

def get_url_archivo(nombre_archivo, mapa_df):
    fila = mapa_df[mapa_df["nombre_archivo"] == nombre_archivo]
    if not fila.empty:
        file_id = fila.iloc[0]["id_archivo"]
        return f"https://drive.google.com/uc?id={file_id}&export=download"
    else:
        st.warning(f"⚠️ Archivo '{nombre_archivo}' no se encontró en el mapa.")
        return None

# ID del archivo mapa_archivos.csv en Google Drive
ID_MAPA = "12TQGeBaLBM8ZIMCTv9ippkPW49hMACAi"

# Cargar el mapa
mapa = cargar_mapa_archivos(ID_MAPA)

# Selector de archivo
archivo_seleccionado = st.selectbox("Selecciona un archivo para visualizar", mapa["nombre_archivo"].dropna())

# Obtener URL y cargar CSV
url = get_url_archivo(archivo_seleccionado, mapa)
if url:
    try:
        df = pd.read_csv(url)
        st.success(f"✅ Archivo cargado: {archivo_seleccionado}")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {e}")
