import streamlit as st
import pandas as pd
from pyxlsb import open_workbook

# -----------------------------------------------
# Configuración de página y logo
# -----------------------------------------------
st.set_page_config(page_title="Dashboard de Packsys", layout="wide")
st.image("packsys_logo.png", width=200)

# Simulación de login
st.success("Inicio de sesión exitoso")

# -----------------------------------------------
# Selector principal
# -----------------------------------------------
seccion = st.radio("Selecciona una opción:", ["Existencias", "Detalle", "Archivo"], horizontal=False)

# -----------------------------------------------
# Función utilitaria para leer hoja XLSB
# -----------------------------------------------
@st.cache_data(show_spinner=False)
def read_xlsb(path: str, sheet: str) -> pd.DataFrame:
    """Lee una hoja de un XLSB y devuelve un DataFrame."""
    data = []
    with open_workbook(path) as wb:
        with wb.get_sheet(sheet) as sh:
            for row in sh.rows():
                data.append([c.v for c in row])
    return pd.DataFrame(data[1:], columns=data[0])

# Ruta del archivo (debe estar en el repositorio)
XLSB_PATH = "Analisis de Existencias PSM y PSD.xlsb"

# Extraer nombres de hojas disponibles (una sola vez)
@st.cache_data
def get_sheet_names(path: str):
    with open_workbook(path) as wb:
        return list(wb.sheets)

# =================================================
# Bloque EXISTENCIAS (placeholder)
# =================================================
if seccion == "Existencias":
    st.subheader("📦 Existencias")
    st.info("Aquí irá el análisis de existencias (pendiente de implementar).")

# =================================================
# Bloque DETALLE (placeholder)
# =================================================
elif seccion == "Detalle":
    st.subheader("📋 Detalle")
    st.warning("Bloque 'Detalle' aún en desarrollo.")

# =================================================
# Bloque ARCHIVO (visualización editable)
# =================================================
else:
    st.subheader("📁 Visualización editable del archivo XLSB")

    try:
        hojas = get_sheet_names(XLSB_PATH)
        hoja_sel = st.selectbox("Selecciona la hoja:", hojas, index=0)

        df = read_xlsb(XLSB_PATH, hoja_sel)
        st.markdown("🛠 **Puedes editar los valores en la tabla (no se guarda en el archivo original).**")
        df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        st.dataframe(df_editado, use_container_width=True, height=550)

    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
