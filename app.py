# app.py
import streamlit as st
import pandas as pd

# --- Configuración inicial ---
st.set_page_config(page_title="Consulta de Existencias - Packsys", layout="wide")

# --- Encabezado con logo ---
st.image("packsys_logo.png", width=300)

st.title("Consulta de Existencias de Producto")

# --- Cargar archivos ---
@st.cache_data
def cargar_datos():
    df_existencias = pd.read_csv("Existencias Inventario Disponible Localizador.csv", encoding="utf-8-sig")
    df_unificacion = pd.read_excel("Unificación de claves.xlsx")
    df_psd = pd.read_excel("PSD multiplicacion de claves.xlsx")
    df_catalogo = pd.read_csv("Catalogo de Productos.csv", encoding="utf-8-sig")
    return df_existencias, df_unificacion, df_psd, df_catalogo

df_existencias, df_unificacion, df_psd, df_catalogo = cargar_datos()

# --- Procesamiento ---
def preparar_datos():
    # Limpiar claves
    df_existencias["Nombre de artículo"] = df_existencias["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
    df_unificacion["Nombre de artículo"] = df_unificacion["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
    df_psd["Nombre del articulo"] = df_psd["Nombre del articulo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)
    df_catalogo["Nombre de artículo"] = df_catalogo["Nombre de artículo"].astype(str).str.strip().str.replace(r"\.$", "", regex=True)

    # Merge claves
    df = df_existencias.merge(df_unificacion, on="Nombre de artículo", how="left")
    df["Item principal"] = df["Item principal"].fillna(df["Nombre de artículo"])

    df = df.merge(df_psd.rename(columns={"Nombre del articulo": "Nombre de artículo"}), on="Nombre de artículo", how="left")
    df["Clave Origen"] = df["Clave Origen"].fillna(df["Item principal"])
    df["Clave Consolidada"] = df["Clave Origen"]

    # Cantidades
    df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors='coerce')
    df["Multiplo con base en UM Clave Origen"] = pd.to_numeric(df["Multiplo con base en UM Clave Origen"], errors='coerce').fillna(1)
    df["Cantidad Ajustada"] = df["Cantidad"] * df["Multiplo con base en UM Clave Origen"]

    # Almacenes
    df["Organización de inventario"] = df["Organización de inventario"].astype(str).str.strip().str.upper()
    plataformas = ["MERCADO_LIBRE", "AMAZON"]
    disponibles = ["PSD_CAT", "LOGISTORAGE_MTY", "DHL_CAT", "CUAUTIPARKII", "WHM_MRD", "DHL_PUEBLA", "DHL_GDL", "LOGISTORAGE_TIJ"]
    df["Tipo de Existencia"] = df["Organización de inventario"].apply(
        lambda x: "Existencia en plataformas" if x in plataformas else
                  "Existencia disponible" if x in disponibles else
                  f"Otro ({x})")

    # Merge catálogo
    df = df.merge(df_catalogo[["Nombre de artículo", "PK_PZASTARIMA", "PZAS/PAQUETE"]], on="Nombre de artículo", how="left")

    # Conversiones
    df["Piezas"] = df["Cantidad Ajustada"]
    df["Tarimas"] = df["Piezas"] / df["PK_PZASTARIMA"]
    df["Paquetes"] = df["Piezas"] / df["PZAS/PAQUETE"]
    df[["Tarimas", "Paquetes"]] = df[["Tarimas", "Paquetes"]].where(df[["Tarimas", "Paquetes"]] > 0)

    return df

df_datos = preparar_datos()

# --- Entrada de usuario ---
clave = st.text_input("Ingrese la clave del producto a consultar:")

if clave:
    clave = clave.strip()
    filtrado = df_datos[df_datos["Clave Consolidada"].astype(str) == clave]

    if not filtrado.empty:
        st.success(f"✅ Existencias para la clave: {clave}")
        stock_total = filtrado["Cantidad Ajustada"].sum()
        st.metric("Total unidades disponibles", f"{stock_total:,.0f}")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📦 Detalle por Almacén")
            st.dataframe(
                filtrado.groupby("Organización de inventario")[["Cantidad Ajustada", "Piezas", "Tarimas", "Paquetes"]].sum()
            )

        with col2:
            st.subheader("📊 Existencias por Tipo")
            st.dataframe(
                filtrado.groupby("Tipo de Existencia")[["Cantidad Ajustada"]].sum()
            )

        st.subheader("🔄 Conversión por Tipo de Existencia")
        for tipo in ["Existencia disponible", "Existencia en plataformas"]:
            df_tipo = filtrado[filtrado["Tipo de Existencia"] == tipo]
            if not df_tipo.empty:
                st.markdown(f"**{tipo}**")
                st.write(f"- 🧩 Piezas: {df_tipo['Piezas'].sum():,.2f}")
                st.write(f"- 🏗️ Tarimas: {df_tipo['Tarimas'].sum():,.2f}")
                st.write(f"- 📦 Paquetes: {df_tipo['Paquetes'].sum():,.2f}")
    else:
        st.error("❌ No se encontraron existencias para esa clave.")
