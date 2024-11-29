# Script que extrae REDI y UTI de SAP según una lista de proyectos de un excel
import win32com.client
import pandas as pd
from datetime import datetime
import subprocess
import openpyxl
import pygetwindow as gw
import time
import os
import glob
import numpy as np
# Marca el inicio del tiempo
start_time = time.time()
# Obtener la fecha actual en el formato deseado
FECHA = datetime.now().strftime('%d-%m-%y')

TEMPORADA = "2024-2"

# Define la ubicación del directorio donde se guardarán los archivos Excel
output = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\CACHE\\'+TEMPORADA
output_DATA = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\'+TEMPORADA

# Elimina todos los archivos Excel en la ubicación especificada
excel_files = glob.glob(os.path.join(output_DATA, '*.xlsx'))
for excel_file in excel_files:
    os.remove(excel_file)
    
# Obtener la lista de archivos REDI y UTI en la carpeta CACHE
redi_files = glob.glob(os.path.join(output, 'REDI *.xlsx'))
uti_files = glob.glob(os.path.join(output, 'UTI *.xlsx'))

# Función para combinar archivos Excel
def combine_files(files, output_file):
    combined_df = pd.DataFrame()
    for file in files:
        df = pd.read_excel(file)
        if not df.empty:
            # Eliminar las filas donde la columna "PROYECTO" esté vacía
            df = df.dropna(subset=["Grafo"])
        # Agregar el DataFrame al combinado
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    # Guardar el DataFrame combinado en un archivo Excel
    combined_df.to_excel(output_file, index=False)

# Combinar y guardar los archivos REDI
combine_files(redi_files, os.path.join(output_DATA, 'REDI.xlsx'))

# Combinar y guardar los archivos UTI
combine_files(uti_files, os.path.join(output_DATA, 'UTI.xlsx'))

# Leer el archivo de Excel que contiene la lista de proyectos
bd_file = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\BD.xlsx'
materiales_file = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\Recursos\\Materiales.xlsx'
df_bd = pd.read_excel(bd_file, sheet_name=TEMPORADA)
df_materiales = pd.read_excel(materiales_file, sheet_name='MATERIALES').drop("Desc.Corta", axis=1)
df_materiales = df_materiales.drop_duplicates(subset='Material')


#Lee los archivos de utilitarios y REDIS creado y almacena la información en dos dataframe
file_REDI = os.path.join(output_DATA,'REDI.xlsx')
df_REDI = pd.read_excel(file_REDI)

file_UTI = os.path.join(output_DATA, 'UTI.xlsx')
df_UTI = pd.read_excel(file_UTI).drop_duplicates()

# Cambiar el nombre de la columnas
df_UTI.rename(columns={'Operación': 'Oper.'}, inplace=True)
df_UTI.rename(columns={'Descripción Operación': 'Denom.Operación'}, inplace=True)
df_UTI.rename(columns={'Precio': 'MOD'}, inplace=True)
df_UTI.rename(columns={'Proyecto': 'PEP'}, inplace=True)
df_UTI.rename(columns={'Nom. Proyecto': 'Proyecto'}, inplace=True)
df_REDI.rename(columns={'Imp.Estimado': 'MAT Estimado'}, inplace=True)
df_REDI.rename(columns={'Importe Despacho': 'MAT Despachado'}, inplace=True)

print(df_UTI)

###AÑADIR  COLUMNAS DE HH TUBO Y PESO #####
# Ambas columnas 'Material' sean de tipo str ##DEBIDO A CODIGO BSU (SEGUNDO USO)
df_REDI['Material'] = df_REDI['Material'].astype(str)
df_materiales['Material'] = df_materiales['Material'].astype(str)
###########################################################################################
# Función que agrega ceros solo si el valor es numérico
def format_oper(value):
    value_str = str(value)  # Asegura que el valor sea una cadena
    if value_str.isdigit():  # Verifica si el valor es numérico
        return value_str.zfill(4)  # Agrega ceros a la izquierda si es numérico
    else:
        return value_str  # Si no es numérico, deja el valor tal cual

# Aplicar la función a ambas columnas 'Oper.'
df_REDI['Oper.'] = df_REDI['Oper.'].apply(format_oper)
df_UTI['Oper.'] = df_UTI['Oper.'].apply(format_oper)

# Aplicar la función a ambas columnas 'Oper.'
df_REDI['Oper.'] = df_REDI['Oper.'].apply(format_oper)
df_UTI['Oper.'] = df_UTI['Oper.'].apply(format_oper)
df_REDI['Oper.'] = df_REDI['Oper.'].astype(str)
df_UTI['Oper.'] = df_UTI['Oper.'].astype(str)
df_REDI['Grafo'] = df_REDI['Grafo'].astype(str)
df_UTI['Grafo'] = df_UTI['Grafo'].astype(str)
##########################################################################################

# Unir los DataFrames en base a la columna "Codigo"
df_REDI = pd.merge(df_REDI, df_materiales, on='Material', how='left')

# Calcular la columna "Peso(kg)" multiplicando "Cantidad tomada" por "Factor"
df_REDI['Peso(kg)'] = df_REDI['Cantidad tomada'] * df_REDI['Factor']
df_REDI['Peso estimado(kg)'] = df_REDI['Cantidad'] * df_REDI['Factor']

# Eliminar la columna "Factor" y "Htub" que son las constantes a multiplicar por el material
df_REDI = df_REDI.drop(columns=['Factor'])

################################################################################################
################################################################################################
################################################################################################

selected_columns = df_UTI[["Denom.Operación", "Grafo","Oper.", "Proyecto"]]

# Combinar los DataFrames según las columnas en común
#Se le agrega la columna proyecto al DF de REDI
df_REDI = pd.merge(df_REDI, selected_columns , on=["Denom.Operación", "Grafo","Oper."], how="left")

################################################################################################
################################################################################################
################################################################################################

# Agrupa por nombre y suma los montos de Material
df_1 = df_REDI.groupby(['Denom.Operación', 'Grafo', 'Oper.']).agg({
    'MAT Estimado': 'sum',       # Suma de la columna 'MAT Estimado'
    'MAT Despachado': 'sum'    # Suma de la columna 'Peso(kg)'
}).reset_index()

# Unir el DataFrame redi_data2 al Combined.xlsx
df_UTI = df_UTI.merge(df_1, on=['Denom.Operación','Grafo', 'Oper.'], how='left')
################################################################################################

# Define una función para asignar los valores según las condiciones
def asignar_categoria(elem_pep):
    elem_pep = str(elem_pep)  # Convierte el valor a cadena
    #PANGAS PESQUERA ISA
    if elem_pep.startswith("A.S/0028-224-RP-1"):
        return "PANGA COQUI IX"
    elif elem_pep.startswith("A.S/0028-224-SI"):
        return "PANGA COQUI XII"
    elif elem_pep.startswith("A.S/0028-224-RP-2"):
        return "PANGA COQUI XII"
    elif elem_pep.startswith("A.S/0028-224-RP-3"):
        return "PANGA SAN JUDAS"
    elif elem_pep.startswith("A.S/0028-224-RP-4"):
        return "PANGA COQUI II"
    elif elem_pep.startswith("A.S/0028-224-RP-5"):
        return "PANGA MALAGA I"    
    elif elem_pep.startswith("A.S/0028-224-RP-6"):
        return "PANGA COQUI VI" 
    elif elem_pep.startswith("A.S/0028-224-RP-7"):
        return "PANGA COQUI X" 
    elif elem_pep.startswith("A.S/0028-224-RP-8"):
        return "PANGA SAN JUDAS 2" 
    #TASA
    elif elem_pep.startswith("GP/62-224-MO"):
        return "OPEX"
    elif elem_pep.startswith("GP/60-224-MO"):
        return "OPEX"
    
    elif "PM" in elem_pep:
        return "PROYECTO MEJORA"
    elif "TQ" in elem_pep:
        return "PROYECTO MEJORA"
    elif "RP" in elem_pep:
        return "PANGA"
    elif elem_pep.endswith("GP/62-224-CA-PI-2") or elem_pep.endswith("GP/62-224-CA-AD-1"):
        return "ADITAMENTO"
    elif elem_pep.endswith("GP/60-224-CA-PI-3") or elem_pep.endswith("GP/60-224-CA-AD-2"):
        return "ADITAMENTO"
    elif elem_pep.endswith("GP/46-124-CA-PI-2") or elem_pep.endswith("GP/46-124-CA-AD-1"):
        return "ADITAMENTO"
    elif elem_pep.endswith("GP/51-124-CA-PI-2") or elem_pep.endswith("GP/51-124-CA-AD-1"):
        return "ADITAMENTO" 
    elif elem_pep.endswith("GP/47-124-CA-PI-2") or elem_pep.endswith("GP/47-124-CA-AD-1"):
        return "ADITAMENTO"
    elif elem_pep.endswith("GP/53-224-CA-PI-4") or elem_pep.endswith("GP/53-124-CA-PI-2"):
        return "ADITAMENTO"
    elif elem_pep.endswith("GP/56-124-CA-PI-2") or elem_pep.endswith("GP/56-124-CA-AD-1"):
        return "ADITAMENTO"
    
    
    elif "PG" in elem_pep:
        return "PROPULSION Y GOBIERNO"
    elif "SA" in elem_pep:
        return "SISTEMAS AUXILIARES"
    elif "EM" in elem_pep:
        return "EMERGENCIA"

    #TERCEROS
    elif "CE" in elem_pep:
        return "CASCO"        
    elif elem_pep.endswith("CA"):
        return "ADITAMENTO"
    elif elem_pep.endswith("EM"):
        return "EMERGENCIA"
    elif elem_pep.endswith("LI"):
        return "CASCO"
    elif elem_pep.endswith("PG"):
        return "PROPULSION Y GOBIERNO"
    elif elem_pep.endswith("SA"):
        return "SISTEMAS AUXILIARES"
    elif elem_pep.endswith("SI"):
        return "CASCO"

    else:
        return "CASCO"  # Si no cumple con ninguna condición

# Aplica la función a la columna "Elem.PEP" y crea una nueva columna "Categoría"
df_UTI['Categoría'] = df_UTI['Elem.PEP'].apply(asignar_categoria)
################################################################################################

# Se deja la columna del valor cambiado como USD para hacer seguimiento de que ese valor antes era USD
df_UTI['MOD'] =  df_UTI.apply(lambda row: row['MOD'] * 3.7 if row['Moneda'] == 'USD' else row['MOD'], axis=1)

# Eliminar las filas donde la columna 'Proyecto' está vacía
df_UTI =  df_UTI.dropna(subset=['Proyecto'])

#Añadir categória a las REDI

selected_columns = df_UTI[["Denom.Operación", "Grafo","Oper.", "Categoría"]]

# Combinar los DataFrames según las columnas en común
#Se le agrega la columna CATEGORIA al DF de REDI
df_REDI = pd.merge(df_REDI, selected_columns , on=["Denom.Operación", "Grafo","Oper."], how="left")

################################################################################################
################################################################################################
################################################################################################

# Guardar el resultado de df1 en el archivo Excel, especificando la hoja que deseas actualizar
with pd.ExcelWriter(file_REDI, mode='a', if_sheet_exists='replace') as writer:
    df_REDI.to_excel(writer, sheet_name='Sheet1', index=False)

# Guardar el resultado de df1 en el archivo Excel, especificando la hoja que deseas actualizar
with pd.ExcelWriter(file_UTI, mode='a', if_sheet_exists='replace') as writer:
    df_UTI.to_excel(writer, sheet_name='Sheet1', index=False)
# Marca el final del tiempo
end_time = time.time()

# Calcula el tiempo transcurrido y lo imprime en consola
execution_time = (end_time - start_time)/60
print(f"El script demoró {execution_time:.2f} minutos en ejecutarse.")