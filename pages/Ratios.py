import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
import altair as alt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
# Fecha actual
FECHA = datetime.now().strftime('%d-%m-%y')

# Configuración de la página
st.set_page_config(
    page_title="Control de Proyectos",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ruta al archivo de Excel
BD = './BD.xlsx'

# Cargar el libro de trabajo y las hojas disponibles
TEMPORADAS = load_workbook(BD, read_only=True).sheetnames

selector_temporada = st.sidebar.selectbox("Seleccione la temporada:", TEMPORADAS, index=0)
df_proyecto = pd.read_excel(BD, sheet_name=selector_temporada)

df_proyecto = df_proyecto[df_proyecto['Temporada'].isin([selector_temporada])]

# Ruta al archivo de Excel
UTI = './'+selector_temporada+'/UTI.xlsx'
df_UTI = pd.read_excel(UTI, sheet_name="Sheet1")

# Reemplazar valores N/A (NaN) con ceros
df_UTI = df_UTI.fillna(0)

REDI = './'+selector_temporada+'/REDI.xlsx'
df_REDI = pd.read_excel(REDI, sheet_name="Sheet1")

df_1= df_UTI.groupby(['Proyecto','Categoría'])['MAT Estimado'].sum().reset_index()
df_1['MAT Estimado']= df_1['MAT Estimado']/1000
df_2= df_UTI.groupby(['Proyecto','Categoría'])['MOD'].sum().reset_index()
df_2['MOD']= df_2['MOD']/1000
df_ratio = pd.merge(df_1, df_2, on=['Proyecto','Categoría'], how='outer')

selector_nave = st.sidebar.selectbox("Seleccione categoria:", df_proyecto['Nave'].drop_duplicates(),index=0)
print(selector_nave)

#Se aplica el filtro de tipo de NAVE
df_proyecto = df_proyecto[df_proyecto['Nave'].isin([selector_nave])]
df = df_ratio[df_ratio['Proyecto'].isin(df_proyecto['Proyecto'])] #Se filtra en el df general según las naves selecionadas
LIST=[]
if selector_nave:
    if selector_nave=="Panga":
        LIST=["PANGA"]
    else:
        LIST= ['CASCO','ADITAMENTO']

selector_categoria = st.sidebar.multiselect("Seleccione categoria:", LIST)
if selector_categoria:
    if selector_categoria==["CASCO"]:
        df = df[df['Categoría'].isin(["CASCO"])]
    elif selector_categoria==['ADITAMENTO']:
        df = df[~df['Categoría'].isin(["CASCO","SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]
    else:
        df = df[~df['Categoría'].isin(["SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]
else:
    st.warning("No se seleccionaron categorías.Mostrando el proyecto total")
    
print("df---------------------------------------------------------")
print(df)    
df = df.drop(columns=['Categoría'])
df = df.groupby("Proyecto", as_index=False).sum()
df = df.query("`MAT Estimado` > 0 and MOD > 0")

# Verificar que las columnas necesarias existen
if 'MOD' in df and 'MAT Estimado' in df:
    # Crear un scatter plot interactivo con Plotly Express
    scatter_plot = px.scatter(
        df,
        x='MOD',
        y='MAT Estimado',
        color='Proyecto',
        size_max=15,
        hover_data={'Proyecto': True, 'MOD': True, 'MAT Estimado': True},
        labels={'MOD': 'Costo Mano de Obra (Miles)', 'MAT Estimado': 'Costo Material (Miles)'},
        title='Relación entre MOD y Material'
    )
    
    # Calcular la regresión lineal
    x = df['MOD']
    y = df['MAT Estimado']
    coeffs = np.polyfit(x, y, deg=1)  # Ajuste lineal
    slope, intercept = coeffs[0], coeffs[1]
    reg_line = slope * x + intercept  # Línea de regresión

    # Añadir la línea de regresión al gráfico
    scatter_plot.add_trace(
        go.Scatter(
            x=x,
            y=reg_line,
            mode='lines',
            name='Línea de Regresión',
            line=dict(color='red', dash='dash'),
        )
    )

    # Agregar la ecuación de la regresión como anotación
    equation_text = f"Ecuación: y = {slope:.2f}x + {intercept:.2f}"
    scatter_plot.add_annotation(
        x=max(x),  # Posición en el eje X
        y=max(reg_line),  # Posición en el eje Y
        text=equation_text,
        showarrow=False,
        font=dict(size=12, color="black"),
        align="right",
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="black",
    )

    # Configurar el diseño del gráfico
    scatter_plot.update_layout(
        xaxis_title="Costo Mano de Obra (Miles)",
        yaxis_title="Costo Material (Miles)",
        width=800,
        height=600,
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(scatter_plot, use_container_width=True)
else:
    st.error("No se encontraron las columnas 'MOD' y 'MAT Estimado' en los datos.")