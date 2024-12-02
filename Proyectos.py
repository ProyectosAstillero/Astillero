import streamlit as st
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
import altair as alt
import numpy as np
from streamlit_extras.colored_header import colored_header
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

# Configuración de la barra lateral
st.sidebar.header('Proyectos :anchor:')
selector_temporada = st.sidebar.selectbox("Seleccione la temporada:", TEMPORADAS, index=0)
df_proyecto = pd.read_excel(BD, sheet_name=selector_temporada)

# Mostrar opciones para seleccionar proyectos
selector_proyecto = st.sidebar.multiselect("Seleccione proyectos:", df_proyecto['Proyecto'].drop_duplicates())
selector_materiales = st.sidebar.select_slider(
    "Materiales:",
    options=["Estimado","Despachado",])

if selector_materiales=="Estimado":
    MAT = 'MAT Estimado'
    PESO = 'Peso estimado(kg)'
    CTD = 'Cantidad'
else:
    MAT = 'MAT Despachado'
    PESO = 'Peso(kg)'
    CTD = 'Cantidad tomada'

precio_dolar = st.sidebar.slider("Precio del dólar:",min_value=3.00, max_value=4.00, value=3.75, step=0.05,)

# Título de la aplicación
st.title(":ship: Control de proyectos")

# Ruta al archivo de Excel
UTI = './'+selector_temporada+'/UTI.xlsx'
df_UTI = pd.read_excel(UTI, sheet_name="Sheet1")

# Reemplazar valores N/A (NaN) con ceros
df_UTI = df_UTI.fillna(0)

REDI = './'+selector_temporada+'/REDI.xlsx'
df_REDI = pd.read_excel(REDI, sheet_name="Sheet1")

#SUMA DE ACERO

df_peso= df_REDI.groupby(['Proyecto','Categoría'])[PESO].sum().reset_index()

df_soldadura= df_REDI[df_REDI['Desc.Corta'].str.startswith('SOLDADURA', na=False)]
df_soldadura= df_soldadura.groupby(['Proyecto','Categoría'])[CTD].sum().reset_index()
df_soldadura.rename(columns={CTD: 'Soldadura(kg)'}, inplace=True)

df_alambre= df_REDI[df_REDI['Desc.Corta'].str.startswith('ALAMBRE', na=False)]
df_alambre= df_alambre.groupby(['Proyecto','Categoría'])[CTD].sum().reset_index()
df_alambre.rename(columns={CTD: 'Alambre tub(kg)'}, inplace=True)

df_oxigeno= df_REDI[df_REDI['Desc.Corta'].isin(['OXIGENO IND.'])]
df_oxigeno= df_oxigeno.groupby(['Proyecto','Categoría'])[CTD].sum().reset_index()
df_oxigeno.rename(columns={CTD: 'Oxígeno(m3)'}, inplace=True)

#selector_radio =[]
#radio = st.sidebar.radio("Seleccione para cálculo de Acero y ratios:",
#                ["CASCO", "ADITAMENTO", "CASCO + ADITAMENTOS"],index=2)
#if radio =="CASCO":
#    selector_radio = ['CASCO']
#if radio =="ADITAMENTO":
#    selector_radio = ['ADITAMENTO']
#if radio =="CASCO + ADITAMENTOS":
#    selector_radio = ['ADITAMENTO','CASCO']


df_ratio = pd.merge(df_peso, df_soldadura, on=['Proyecto','Categoría'], how='outer')
df_ratio = pd.merge(df_ratio, df_alambre, on=['Proyecto','Categoría'], how='outer')
df_ratio = pd.merge(df_ratio, df_oxigeno, on=['Proyecto','Categoría'], how='outer')
df_ratio['Soldadura Total(kg)'] = (df_ratio['Soldadura(kg)']+df_ratio['Alambre tub(kg)']*1.67)
        
# Verifica si hay proyectos seleccionados
if selector_proyecto:
 for proyecto in selector_proyecto:

        df_peso = df_peso[df_peso['Proyecto'] == proyecto]
        df_soldadura = df_soldadura[df_soldadura['Proyecto'] == proyecto]
        df_alambre = df_alambre[df_alambre['Proyecto'] == proyecto]   
        df_oxigeno = df_oxigeno[df_oxigeno['Proyecto'] == proyecto] 
        
        colored_header(label=proyecto,
        color_name="violet-70")
        
        # Filtrar datos del proyecto seleccionado
        df_general = df_UTI[df_UTI['Proyecto'] == proyecto]
        df1= df_general.groupby(['Proyecto'])['MOD'].sum().reset_index()
        df2= df_general.groupby(['Proyecto'])[MAT].sum().reset_index()
        result = pd.merge(df1, df2, on='Proyecto')
        result['Total'] = result['MOD'] + result[MAT]
        result['Total USD'] = result['Total'] / precio_dolar
        
        # Dar formato de moneda a los datos
        formatted_result = result.style.format({'MOD': 'S/. {:,.2f}', MAT: 'S/. {:,.2f}', 'Total': 'S/. {:,.2f}', 'Total USD': '$. {:,.2f}'})

        # Mostrar el DataFrame en Streamlit
        st.dataframe(formatted_result,hide_index=True, use_container_width=True)

        #Costos x PEP
        df_PEP = df_general['Categoría'].dropna().drop_duplicates().sort_values()
        df_PEP2 = df_general.groupby(['Categoría'])['MOD'].sum().reset_index()
        df_PEP3 = df_general.groupby(['Categoría'])[MAT].sum().reset_index()
        result2 = pd.merge(df_PEP2, df_PEP3, on='Categoría')
        result2['Total'] = result2['MOD'] + result2[MAT]
        result2['Total USD'] = result2['Total'] / precio_dolar

        # Dar formato de moneda a los datos
        formatted_result = result2.style.format({'MOD': 'S/. {:,.2f}', MAT: 'S/. {:,.2f}', 'Total': 'S/. {:,.2f}', 'Total USD': '$. {:,.2f}'})
        st.dataframe(formatted_result,hide_index=True, use_container_width=True)
        

        df_ratio_proyecto = df_ratio[df_ratio['Proyecto'] == proyecto]
        
        st.subheader("Acero")
        col1, col2 =st.columns([0.5,0.5])
        with col1:
            st.dataframe(df_ratio_proyecto, use_container_width=False,column_config={
                        "Proyecto": None,
                        "Soldadura(kg)": None,
                        "Alambre tub(kg)": None,
                        PESO: st.column_config.NumberColumn(
                            "Peso(kg)",
                            format="%.2f kg",
                            width=None,
                        )

                    },hide_index=True)
        
        with col2:
            chart = alt.Chart(df_ratio_proyecto).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field=PESO, type="quantitative", title="Peso (kg)"),
            color=alt.Color(field="Categoría", type="nominal", legend=alt.Legend(title="Categorías")),
            tooltip=["Categoría", alt.Tooltip(PESO, title="Peso (kg)")]
            ).properties(
                width=300,
                height=300
            )
            
            # Mostrar el gráfico
            st.altair_chart(chart, use_container_width=True)
              
else:
    st.info("Por favor, seleccione uno o más proyectos para ver los detalles.")
    
