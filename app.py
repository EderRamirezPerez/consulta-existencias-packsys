import streamlit as st
import streamlit.components.v1 as components

# -----------------------------------------------
# Configuración visual
# -----------------------------------------------
st.set_page_config(page_title="Dashboard de Packsys", layout="wide")
st.image("packsys_logo.png", width=200)

# Inicio de sesión simulado (placeholder)
st.success("Inicio de sesión exitoso")

# -----------------------------------------------
# Menú principal
# -----------------------------------------------
seccion = st.radio("Selecciona una opción:", ["Existencias", "Detalle", "Archivo"], horizontal=False)

# ===============================================
# EXISTENCIAS (placeholder)
# ===============================================
if seccion == "Existencias":
    st.subheader("📦 Existencias")
    st.info("Aquí irá el análisis de existencias (pendiente de implementar).")

# ===============================================
# DETALLE (placeholder)
# ===============================================
elif seccion == "Detalle":
    st.subheader("📋 Detalle")
    st.warning("Bloque 'Detalle' aún en desarrollo.")

# ===============================================
# ARCHIVO (iframe Google Sheets estilo Excel)
# ===============================================
else:
    st.subheader("📁 Visualización del libro en Google Sheets (modo vista)")

    sheet_url = (
        "https://docs.google.com/spreadsheets/d/"
        "1_9ZBLqZbHOlFTtInZAbju7g3NU20NqMY/preview"
    )

    components.iframe(sheet_url, height=700, scrolling=True)
    st.caption("Los cambios que realices aquí solo viven en la sesión; el archivo en Drive permanece intacto.")
