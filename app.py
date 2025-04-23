import streamlit as st
import pandas as pd
import gdown

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
    st.subheader("📁 Visualización editable del archivo de Drive")

    # ID del archivo de Google Drive
    file_id = "1_9ZBLqZbHOlFTtInZAbju7g3NU20NqMY"
    url = f"https://drive.google.com/uc?id={file_id}"

    # Descargar el archivo cada vez que se ejecuta la app
    output = "archivo.xlsx"
    gdown.download(url, output, quiet=False)

    try:
        hojas = pd.read_excel(output, sheet_name=None)
        nombre_hoja = st.selectbox("Selecciona una hoja para visualizar/modificar:", list(hojas.keys()))
        df_hoja = hojas[nombre_hoja]

        st.markdown("🛠 **Puedes editar los valores en la tabla. Esto no afecta el archivo original en Drive.**")
        df_editado = st.data_editor(df_hoja, use_container_width=True, num_rows="dynamic")
        st.dataframe(df_editado)

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
