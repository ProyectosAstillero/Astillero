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

############################PESOS#########################################
df_acero= df_REDI.groupby(['Proyecto','Categoría'])['Peso estimado(kg)'].sum().reset_index()
df_acero["Peso estimado(kg)"] = df_acero["Peso estimado(kg)"]/1000
df_acero.rename(columns={'Peso estimado(kg)': 'Peso(Tn)'}, inplace=True)

df_soldadura= df_REDI[df_REDI['Desc.Corta'].str.startswith('SOLDADURA', na=False)]
df_soldadura= df_soldadura.groupby(['Proyecto','Categoría'])['Cantidad tomada'].sum().reset_index()
df_soldadura.rename(columns={'Cantidad tomada': 'Soldadura(kg)'}, inplace=True)

df_alambre= df_REDI[df_REDI['Desc.Corta'].str.startswith('ALAMBRE', na=False)]
df_alambre= df_alambre.groupby(['Proyecto','Categoría'])['Cantidad tomada'].sum().reset_index()
df_alambre.rename(columns={'Cantidad tomada': 'Alambre tub(kg)'}, inplace=True)

df_oxigeno= df_REDI[df_REDI['Desc.Corta'].isin(['OXIGENO IND.'])]
df_oxigeno= df_oxigeno.groupby(['Proyecto','Categoría'])['Cantidad tomada'].sum().reset_index()
df_oxigeno.rename(columns={'Cantidad tomada': 'Oxigeno(m3)'}, inplace=True)

df_disco= df_REDI[df_REDI['Desc.Corta'].str.startswith('DISCO', na=False)]
df_disco= df_disco.groupby(['Proyecto','Categoría'])['Cantidad tomada'].sum().reset_index()
df_disco.rename(columns={'Cantidad tomada': 'Discos(pz)'}, inplace=True)

df_ratio_acero = pd.merge(df_acero, df_soldadura, on=['Proyecto','Categoría'], how='outer')
df_ratio_acero = pd.merge(df_ratio_acero, df_alambre, on=['Proyecto','Categoría'], how='outer')
df_ratio_acero = pd.merge(df_ratio_acero, df_oxigeno, on=['Proyecto','Categoría'], how='outer')
df_ratio_acero = pd.merge(df_ratio_acero, df_disco, on=['Proyecto','Categoría'], how='outer')
df_ratio_acero.fillna(0, inplace=True)

df_ratio_acero['SoldxAcero'] = (df_ratio_acero['Soldadura(kg)']+df_ratio_acero['Alambre tub(kg)']*0.6)/df_ratio_acero['Peso(Tn)']
df_ratio_acero['OxigenoxAcero'] = df_ratio_acero['Oxigeno(m3)']/df_ratio_acero['Peso(Tn)']
df_ratio_acero['DiscoxAcero'] = df_ratio_acero['Discos(pz)']/df_ratio_acero['Peso(Tn)']
df_ratio_acero.fillna(0, inplace=True)
######################################################################################################

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
df_ratio_acero = df_ratio_acero[df_ratio_acero['Proyecto'].isin(df_proyecto['Proyecto'])]

LIST=[]
if selector_nave:
    if selector_nave=="Panga":
        LIST=["PANGA"]
    else:
        LIST= ['CASCO','ADITAMENTO']
        

#SE FILTRA SEGÚN SEA CASCO O ADITAMENTOS
selector_categoria = st.sidebar.multiselect("Seleccione categoria:", LIST)
if selector_categoria:
    if selector_categoria==["CASCO"]:
        df = df[df['Categoría'].isin(["CASCO"])]
        df_ratio_acero = df_ratio_acero[df_ratio_acero['Categoría'].isin(["CASCO"])]
        
    elif selector_categoria==['ADITAMENTO']:
        df = df[~df['Categoría'].isin(["CASCO","SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]
        df_ratio_acero = df_ratio_acero[~df_ratio_acero['Categoría'].isin(["CASCO","SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]
    else:
        df = df[~df['Categoría'].isin(["SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]
        df_ratio_acero = df_ratio_acero[~df_ratio_acero['Categoría'].isin(["SISTEMAS AUXILIARES","PROPULSION Y GOBIERNO"])]

else:
    st.warning("No se seleccionaron categorías.Mostrando el proyecto total")
    
  
df = df.drop(columns=['Categoría'])
df = df.groupby("Proyecto", as_index=False).sum()
df = df.query("`MAT Estimado` > 0 and MOD > 0")
df_ratio_acero = df_ratio_acero.query("`Peso(Tn)` > 0")
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

print(df_ratio_acero)

################# Crear un scatter RATIO X ACERO
# Scatter plot con línea de regresión de grado 2
scatter_plot2 = px.scatter(
    df_ratio_acero,
    x='Peso(Tn)',
    y='Soldadura(kg)',
    color='Proyecto',
    size_max=15,
    hover_data={'Proyecto': True, 'Peso(Tn)': True, 'Soldadura(kg)': True},
    labels={'Peso(Tn)': 'Acero instalado (Toneladas)', 'Soldadura(kg)': 'Soldadura empleada (Kg)'},
    title='Relación entre Acero y Soldadura (Regresión Grado 2)'
)

# Calcular la regresión polinómica de grado 2
A = df_ratio_acero['Peso(Tn)']
B = df_ratio_acero['Soldadura(kg)']
coeffs2 = np.polyfit(A, B, deg=2)  # Ajuste polinómico de grado 2
a, b, c = coeffs2  # Coeficientes del polinomio

# Generar valores de la curva
A_sorted = np.sort(A)  # Ordenar X para que la curva sea continua
reg_line2 = a * A_sorted**2 + b * A_sorted + c  # Generar Y usando la ecuación de segundo grado

# Añadir la línea de regresión al gráfico
scatter_plot2.add_trace(
    go.Scatter(
        x=A_sorted,
        y=reg_line2,
        mode='lines',
        name='Línea de Regresión (Grado 2)',
        line=dict(color='red', dash='dash'),
    )
)

# Agregar la ecuación como anotación
equation_text2 = f"Ecuación: y = {a:.2f}x² + {b:.2f}x + {c:.2f}"
scatter_plot2.add_annotation(
    x=A.mean(),  # Posición centrada en el promedio de X
    y=(a * A.mean()**2 + b * A.mean() + c),  # Valor en el promedio de X
    text=equation_text2,
    showarrow=False,
    font=dict(size=12, color="black"),
    align="center",
    bgcolor="rgba(255, 255, 255, 0.7)",
    bordercolor="black",
)

# Configurar el diseño del gráfico
scatter_plot2.update_layout(
    xaxis_title="Peso (Toneladas)",
    yaxis_title="Soldadura (Kg)",
    width=800,
    height=600,
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(scatter_plot2, use_container_width=True)


#########################################################################################
# Lista de las combinaciones de variables para los scatter plots
combos = [
    ('Soldadura(kg)', 'Peso(Tn)', 'Acero y Soldadura'),
    ('Oxigeno(m3)', 'Peso(Tn)', 'Acero y Oxígeno'),
    ('Discos(pz)', 'Peso(Tn)', 'Acero y Discos')
]

# Bucle para generar los scatter plots
for y_column, x_column, title in combos:
    scatter_plot = px.scatter(
        df_ratio_acero,
        x=x_column,
        y=y_column,
        color='Proyecto',
        size_max=15,
        hover_data={'Proyecto': True, x_column: True, y_column: True},
        labels={x_column: f'{x_column} ', y_column: f'{y_column}'},
        title=f'Relación entre {title}'
    )
    
    # Calcular la regresión lineal para cada combinación
    A = df_ratio_acero[x_column]
    B = df_ratio_acero[y_column]
    coeffs = np.polyfit(A, B, deg=1)  # Ajuste lineal
    slope, intercept = coeffs[0], coeffs[1]
    reg_line = slope * A + intercept  # Línea de regresión

    # Añadir la línea de regresión al gráfico
    scatter_plot.add_trace(
        go.Scatter(
            x=A,
            y=reg_line,
            mode='lines',
            name='Línea de Regresión',
            line=dict(color='red', dash='dash'),
        )
    )

    # Agregar la ecuación de la regresión como anotación
    equation_text = f"Ecuación: y = {slope:.2f}x + {intercept:.2f}"
    scatter_plot.add_annotation(
        x=A.mean(),  # Posición centrada en el promedio de X
        y=(slope * A.mean() + intercept),  # Valor en el promedio de X
        text=equation_text,
        showarrow=False,
        font=dict(size=12, color="black"),
        align="center",
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="black",
    )

    # Configurar el diseño del gráfico
    scatter_plot.update_layout(
        xaxis_title=f'{x_column} (Toneladas)',
        yaxis_title=f'{y_column} (kg o pzas)',
        width=800,
        height=600,
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(scatter_plot, use_container_width=True)
