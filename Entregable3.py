import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO  # 👈 necesario para crear archivo Excel en memoria
import os

os.system("cls")
# Configuración de la página
# Se debe instalar el lector de archivos en excel
# pip install openpyxl
st.set_page_config(page_title="Dashboard de ventas", page_icon="📶", layout="wide")
st.title("Ventas trimestre I de 2024")

# st.markdown("""
#     <h2 style='color: #ff5733; font-family: Arial; text-align: center;background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
#         🔧 Análisis de ventas
#     </h2>
# """, unsafe_allow_html=True)

df=pd.read_excel("ventas_supermercado.xlsx",skiprows=1, header=1)

def formato(numero, decimales):
  return f"{numero:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")
# Calcular KPIs
total_ventas = df['Total'].sum()
ingreso_bruto = df['Ingreso bruto'].sum()
promedio_calificacion = df['Calificación'].mean()
# Mostrar KPIs en columnas con formato personalizado
# Crear tres columnas para mostrar los KPIs
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("💰 Total Ventas", f"${formato(total_ventas,0)}")
with col2:
    st.metric("📈 Ingreso Bruto", f"${formato(ingreso_bruto,0)}")
with col3:
    st.metric("⭐ Calificación Promedio", f"{formato(promedio_calificacion,2)}")
with st.sidebar:
    st.header("Filtros")
    # Selección de ciudades y líneas de producto
    ciudades = st.multiselect("Selecciona ciudades:", df['Ciudad'].unique(), default=df['Ciudad'].unique())
    lineas = st.multiselect("Selecciona líneas de producto:", df['Línea de producto'].unique(), default=df['Línea de producto'].unique())
df_filtrado= df[df["Ciudad"].isin(ciudades) & df["Línea de producto"].isin(lineas)]

tab1, tab2, tab3 = st.tabs(["📆 Ventas por Mes", "📦 Por Línea", "📂 Datos"], width="stretch")
with tab1:
    st.subheader("📆 Ventas por Mes")
    df_filtrado["Mes"]= df_filtrado["Fecha"].dt.to_period("M").astype(str)
    df_filtrado["Mes"] = df_filtrado["Fecha"].dt.strftime('%m-%Y')
    ventas_mes=df_filtrado.groupby("Mes")["Total"].sum().sort_index()
    fig1, ax1 = plt.subplots()
    ventas_mes.plot(kind='line', marker='o', ax=ax1, color='teal',title="Tendencia de Ventas Mensuales")
                    
    ax1.set_xlabel("Mes")
    ax1.set_ylabel("Total Ventas")
    ax1.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with tab2:
    st.subheader("📦 Ventas por Línea de Producto")
    ventas_linea=df_filtrado.groupby("Línea de producto")["Total"].sum().sort_values()
    fig2, ax2 = plt.subplots()
    ventas_linea.plot(kind='barh', ax=ax2, color='orange',title="Ventas por línea de producto")
    ax2.set_ylabel("")
    ax2.set_xlabel("Ventas")
    st.pyplot(fig2)

df_filtrado.reset_index(drop=True, inplace=True)
df_filtrado.index= range(1, len(df_filtrado) + 1)
with tab3:
    st.subheader("📂 Datos")
    st.dataframe(df_filtrado)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Ventas')
        # 👉 Botón de descarga
    st.download_button(
      label="⬇️ Descargar datos en Excel",
      data=output.getvalue(),
      file_name="ventas_filtradas.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      )