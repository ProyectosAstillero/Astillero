import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(
    page_title="Control de Proyectos",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ruta donde están los archivos Excel
folder_path = "Avance/2025-1/"  # Cambia a la ruta donde se encuentran los archivos

# Obtener lista de proyectos (archivos Excel en la carpeta)
proyectos = [f for f in os.listdir(folder_path) if f.endswith(".xlsx")]

if proyectos:
    # Crear un diccionario para mapear nombres sin extensión a nombres completos
    proyectos_dict = {os.path.splitext(f)[0]: f for f in proyectos}

    # Sidebar: Seleccionar proyecto
    st.sidebar.title("Seleccionar Proyecto")
    proyecto_seleccionado_nombre = st.sidebar.selectbox(
        "Elige un proyecto", list(proyectos_dict.keys()), key="proyecto"
    )

    # Obtener el nombre completo del archivo seleccionado
    proyecto_seleccionado = proyectos_dict[proyecto_seleccionado_nombre]

    # Cargar las hojas del proyecto seleccionado
    if proyecto_seleccionado:
        file_path = os.path.join(folder_path, proyecto_seleccionado)
        try:
            # Obtener las hojas del archivo
            hojas = pd.ExcelFile(file_path).sheet_names
            
            # Mostrar las hojas en un selectbox en la parte superior
            st.title(f"Proyecto: {proyecto_seleccionado_nombre}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                with st.container(border=True):
                    hoja_seleccionada = st.selectbox("Elige una revisión", hojas, key="hoja")
                    df = pd.read_excel(file_path, sheet_name=hoja_seleccionada)

            with col2:
                with st.container(border=True):
                    # Calcular la suma del producto de las columnas Pond y Avance Programado
                    suma_producto = (df['Pond'] * df['Avance Programado']*100/2).sum()
                    st.metric(label="Avance Programado", value=f"{suma_producto:.2f}%")
            with col3:
                with st.container(border=True):
                    # Calcular la suma del producto de las columnas Pond y Avance Programado
                    suma_producto = (df['Pond'] * df['Avance Real']*100/2).sum()
                    st.metric(label="Avance Real", value=f"{suma_producto:.2f}%")               
                 
               
            # Multiplicar las columnas de porcentaje por 100 para mostrar correctamente los valores
            df['Pond'] = df['Pond'] * 100
            df['Avance Real'] = df['Avance Real'] * 100
            df['Avance Programado'] = df['Avance Programado'] * 100

            # Mostrar los datos de la hoja seleccionada
            if hoja_seleccionada:
                # Filtrar las actividades con Orden 2
                orden_2 = df[df['Orden'] == 2]

                # Crear un data editor para cada actividad de Orden 2
                for i, actividad_orden_2 in orden_2.iterrows():                                                            
                    actividad_principal = actividad_orden_2['Actividades']

                    # Determinar el rango de actividades subordinadas basado en las filas
                    inicio_idx = actividad_orden_2.name

                    # Encontrar el índice de la siguiente jerarquía 2 o el final del archivo
                    fin_idx = inicio_idx + 1
                    while fin_idx < len(df) and df.loc[fin_idx, 'Orden'] != 2:
                        fin_idx += 1

                    # Filtrar actividades subordinadas entre inicio y fin, excluyendo jerarquías superiores
                    subordinadas = df.loc[inicio_idx + 1:fin_idx - 1]
                    subordinadas = subordinadas[subordinadas['Orden'] == 3]

                    # Mostrar encabezado y editor
                    st.subheader(actividad_principal)
                    if not subordinadas.empty:
                        edited_data = st.data_editor(
                            subordinadas, 
                            key=f"editor_{actividad_principal}", 
                            hide_index=True, 
                            disabled=("Pond", "Avance Programado", "F. Inicio", "F. Fin"),
                            column_config={
                                "Orden": None,
                                "Diferencia": None,
                                "Estado": None,
                                "Pond": st.column_config.NumberColumn(format="%.2f%%"),
                                "Avance Real": st.column_config.NumberColumn(format="%.2f%%"),
                                "Avance Programado": st.column_config.NumberColumn(format="%.2f%%")
                            }
                        )

                        # Actualizar el DataFrame con los cambios realizados
                        df.loc[edited_data.index] = edited_data
                    else:
                        st.write("No hay actividades subordinadas disponibles.")

                # Botón para guardar los cambios en el archivo Excel
                if st.sidebar.button("Guardar todos los cambios"):
                    # Dividir las columnas de porcentaje por 100 antes de guardar
                    df['Pond'] = df['Pond'] / 100
                    df['Avance Real'] = df['Avance Real'] / 100
                    df['Avance Programado'] = df['Avance Programado'] / 100

                    # Guardar en el archivo Excel con el nombre de la hoja seleccionada
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, index=False, sheet_name=hoja_seleccionada)
                    st.sidebar.success("¡Cambios guardados exitosamente!")
                       
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
else:
    st.sidebar.warning("No se encontraron archivos.")
    st.warning("Asegúrate de que la carpeta contenga archivos para continuar.")