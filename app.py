import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from openpyxl import load_workbook
from googleapiclient.http import MediaIoBaseDownload

# --- Autenticación con Google Drive ---
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gdrive_service_account"], scopes=["https://www.googleapis.com/auth/drive"])
drive_service = build('drive', 'v3', credentials=creds)

# --- Función para leer el archivo de Drive como Excel ---
def leer_excel_drive(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_excel(fh, sheet_name=None, engine="openpyxl")

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Dashboard de Packsys", layout="wide")
st.image("packsys_logo.png", width=200)

# Simulación de login (puedes reemplazar con control real si usas auth)
st.success("Inicio de sesión exitoso")

# --- Selección de bloques ---
opcion = st.radio("Selecciona una opción:", ["Existencias", "Detalle", "Archivo"])

# --- Lógica por sección ---
if opcion == "Existencias":
    st.subheader("📦 Existencias")
    st.info("Aquí iría el contenido de existencias que ya tienes implementado.")

elif opcion == "Detalle":
    st.subheader("📋 Detalle")
    st.warning("Bloque de 'Detalle' aún en desarrollo.")

elif opcion == "Archivo":
    st.subheader("📁 Visualización editable del archivo 'Analisis de Existencias PSM y PSD.xlsx'")

    archivo_id = "1_9ZBLqZbHOlFTtInZAbju7g3NU20NqMY"

    try:
        hojas = leer_excel_drive(archivo_id)
        nombre_hoja = st.selectbox("Selecciona una hoja para visualizar/modificar:", list(hojas.keys()))
        df_hoja = hojas[nombre_hoja]

        st.markdown("🛠 **Puedes editar los valores en la tabla.** Esto no afecta el archivo en Drive.")

        df_editado = st.data_editor(df_hoja, use_container_width=True, num_rows="dynamic")
        st.dataframe(df_editado)

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
