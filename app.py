import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Consulta de Existencias Packsys", layout="wide")
st.image("https://raw.githubusercontent.com/ederramirezperez/consulta-existencias-packsys/main/packsys_logo.png", width=200)
st.title("🔍 Consulta de existencias por clave consolidada o descripción")

# Funciones para leer archivos
def es_html(texto):
    return "<html" in texto.lower() or "<!doctype" in texto.lower()

def leer_csv_drive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    if es_html(response.text):
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(response.text), encoding="utf-8", on_bad_lines="skip", engine="python")

def leer_excel_drive(file_id):
    url = f"https://drive.google.com/uc?id={file_id}&export=download"
    response = requests.get(url)
    return pd.read_excel(io.BytesIO(response.content), sheet_name=0)

# IDs Drive
id_catalogo = "1doNsIfQbibKJyKjC1PWGrifmDpXqiKZv"
id_existencias = "1Nj9g8E1CJ7euYtHVp_vcbeI6YRKFE0yg"
id_unificacion = "16aIthDrAUr8fFpCdUEXljKRLC3vZ9XLW"
id_psd = "1w2JPGhV-hLZWDFbunX7D4ikmCsWlpzFE"

# Cargar datos
df_existencias = leer_csv_drive(id_existencias)
df_unificacion = leer_excel_drive(id_unificacion)
df_psd = leer_excel_drive(id_psd)
df_catalogo = leer_csv_drive(id_catalogo)

# Limpieza
for col in ["Nombre de artículo"]:
    df_existencias[col] = df_existencias[col].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
    df_unificacion[col] = df_unificacion[col].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
    df_catalogo[col] = df_catalogo[col].astype(str).str.strip().str.replace(r"\.$", "", regex=True)

df_psd["Nombre del articulo"] = df_psd["Nombre del articulo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)

# Merge claves
df_merged = df_existencias.merge(df_unificacion, on="Nombre de artículo", how="left")
df_merged["Item principal"].fillna(df_merged["Nombre de artículo"], inplace=True)
df_merged = df_merged.merge(df_psd.rename(columns={"Nombre del articulo": "Nombre de artículo"}), on="Nombre de artículo", how="left")
df_merged["Clave Origen"].fillna(df_merged["Item principal"], inplace=True)
df_merged["Clave Consolidada"] = df_merged["Clave Origen"]

# Cantidades
df_merged["Cantidad"] = pd.to_numeric(df_merged["Cantidad"], errors="coerce")
df_merged["Multiplo con base en UM Clave Origen"] = pd.to_numeric(df_merged["Multiplo con base en UM Clave Origen"], errors="coerce")
df_merged["Multiplo con base en UM Clave Origen"].fillna(1, inplace=True)
df_merged["Cantidad Ajustada"] = df_merged["Cantidad"] * df_merged["Multiplo con base en UM Clave Origen"]

df_merged["Organización de inventario"] = df_merged["Organización de inventario"].astype(str).str.strip().str.upper()

# Clasificación
plataformas = ["MERCADO_LIBRE", "AMAZON"]
disponibles = ["PSD_CAT", "LOGISTORAGE_MTY", "DHL_CAT", "CUAUTIPARKII", "WHM_MRD", "DHL_PUEBLA", "DHL_GDL", "LOGISTORAGE_TIJ"]
df_merged["Tipo de Existencia"] = df_merged["Organización de inventario"].apply(lambda x:
    "Existencia en plataformas" if x in plataformas else
    "Existencia disponible" if x in disponibles else
    f"Otro ({x})"
)

# Merge catálogo
df_merged = df_merged.merge(df_catalogo[[
    "Nombre de artículo",
    "Descripción de artículo",
    "Artículo - Unidad de medida principal",
    "PK_PZASTARIMA",
    "PZAS/PAQUETE"
]], on="Nombre de artículo", how="left")

# Conversión
def calcular_conversiones(row):
    piezas = row["Cantidad Ajustada"]
    tarima = row["PK_PZASTARIMA"]
    paquete = row["PZAS/PAQUETE"]
    return pd.Series([
        piezas,
        piezas / tarima if pd.notna(tarima) and tarima > 0 else None,
        piezas / paquete if pd.notna(paquete) and paquete > 0 else None
    ])

df_merged[["Piezas", "Tarimas", "Paquetes"]] = df_merged.apply(calcular_conversiones, axis=1)

# Agrupaciones
df_stock_real = df_merged.groupby(["Clave Consolidada", "Organización de inventario"], as_index=False)[
    ["Cantidad Ajustada", "Piezas", "Tarimas", "Paquetes"]].sum()
df_existencias_tipo = df_merged.groupby(["Clave Consolidada", "Tipo de Existencia"], as_index=False)["Cantidad Ajustada"].sum()

# ------------------ Interfaz ------------------
col1, col2 = st.columns(2)
clave_input = col1.text_input("🔑 Buscar por Clave Consolidada:")
desc_input = col2.text_input("📝 Buscar por Descripción (parte del texto):")

clave_seleccionada = None

if desc_input:
    desc_input = desc_input.strip().lower()
    opciones = df_catalogo[df_catalogo["Descripción de artículo"].str.lower().str.contains(desc_input)]
    if not opciones.empty:
        desc_elegida = st.selectbox("📌 Coincidencias encontradas:", opciones["Descripción de artículo"].unique())
        fila = opciones[opciones["Descripción de artículo"] == desc_elegida].iloc[0]
        clave_seleccionada = fila["Nombre de artículo"]
        st.success(f"🔗 Clave encontrada: {clave_seleccionada}")
    else:
        st.warning("❌ No se encontraron coincidencias con esa descripción.")

if clave_input:
    clave_seleccionada = clave_input.strip()

if clave_seleccionada:
    resultado = df_stock_real[df_stock_real["Clave Consolidada"] == clave_seleccionada]
    resultado_tipo = df_existencias_tipo[df_existencias_tipo["Clave Consolidada"] == clave_seleccionada]
    df_filtrado = df_merged[df_merged["Clave Consolidada"] == clave_seleccionada]

    if not resultado.empty:
        st.success(f"✅ Existencias reales de '{clave_seleccionada}': {resultado['Cantidad Ajustada'].sum():,.2f} unidades")

        st.subheader("📦 Desglose por almacén")
        st.dataframe(resultado)

        st.subheader("📊 Existencias por tipo")
        st.dataframe(resultado_tipo)

        for tipo in ["Existencia disponible", "Existencia en plataformas"]:
            df_tipo = df_filtrado[df_filtrado["Tipo de Existencia"] == tipo]
            piezas = df_tipo["Piezas"].sum()
            tarimas = df_tipo["Tarimas"].sum()
            paquetes = df_tipo["Paquetes"].sum()

            st.markdown(f"### 🔄 Conversión de unidades - {tipo}")
            st.markdown(f"- 🧩 **Piezas**: {piezas:,.2f}")
            st.markdown(f"- 🏗️ **Tarimas**: {tarimas:,.2f}")
            st.markdown(f"- 📦 **Paquetes**: {paquetes:,.2f}")
    else:
        st.warning(f"⚠️ No se encontraron existencias para '{clave_seleccionada}'.")
