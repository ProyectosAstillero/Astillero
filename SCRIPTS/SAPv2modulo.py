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

TEMPORADA = "2024-1"

# Define la ubicación del directorio donde se guardarán los archivos Excel
output = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\CACHE\\'+TEMPORADA
output_DATA = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\'+TEMPORADA

# Elimina todos los archivos Excel en la ubicación especificada
excel_files = glob.glob(os.path.join(output, '*.xlsx'))
for excel_file in excel_files:
    os.remove(excel_file)

# Leer el archivo de Excel que contiene la lista de proyectos
bd_file = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\BD.xlsx'
materiales_file = 'C:\\Users\\barevalo\\OneDrive - Tecnológica de Alimentos S.A\\Balois -2024\\GITHUB CP\\Recursos\\Materiales.xlsx'
df_bd = pd.read_excel(bd_file, sheet_name=TEMPORADA)
df_materiales = pd.read_excel(materiales_file, sheet_name='MATERIALES').drop("Desc.Corta", axis=1)
df_materiales = df_materiales.drop_duplicates(subset='Material')

# Obtener la lista de PEPs desde la columna 'PEP'
REDI_list = df_bd['REDI'].dropna().unique()
UTI_list = df_bd['UTI'].dropna().unique()

SapGuiAuto = win32com.client.GetObject('SAPGUI')
application = SapGuiAuto.GetScriptingEngine
connection = application.Children(0)
session = connection.Children(0)

for PEP in REDI_list:
    # Crear una nueva variable sin el sufijo
    PEP_SIMPLE = PEP.split("-")[0]
    #PEP_NUMERO = PEP.split("-")[1]
    # Crear una nueva variable sin el /
    NAME = PEP.replace("/", "")
    NAME = NAME + ' ' + FECHA + '.xlsx'
    REDI_NAME = 'REDI ' + NAME
    session.findById('wnd[0]').maximize()
    session.findById('wnd[0]/tbar[0]/okcd').text = 'ZMMR0097'
    session.findById('wnd[0]').sendVKey(0)
    session.findById('wnd[0]/usr/ctxtSO_WERKS-LOW').text = 'TAST'
    session.findById('wnd[0]/usr/ctxtSO_LGORT-LOW').text = 'L001'
    session.findById('wnd[0]/usr/ctxtSO_PS_PS-LOW').text = PEP
    session.findById('wnd[0]/usr/ctxtSO_PS_PS-LOW').setFocus()
    session.findById('wnd[0]/usr/ctxtSO_PS_PS-LOW').caretPosition = 9
    session.findById('wnd[0]').sendVKey(0)
    session.findById('wnd[0]/tbar[0]/btn[0]').press()
    session.findById('wnd[0]/tbar[1]/btn[8]').press()
    session.findById('wnd[0]/usr/cntlGRID1/shellcont/shell').setCurrentCell(-1, 'ZZOBJ1')
    session.findById('wnd[0]/usr/cntlGRID1/shellcont/shell').selectColumn('ZZOBJ1')
    session.findById('wnd[0]/tbar[1]/btn[28]').press()
    session.findById('wnd[0]/mbar/menu[0]/menu[1]/menu[1]').select()
    session.findById('wnd[1]/usr/ctxtDY_PATH').setFocus()
    session.findById('wnd[1]/usr/ctxtDY_PATH').caretPosition = 0
    session.findById('wnd[1]').sendVKey(4)
    session.findById('wnd[2]/usr/ctxtDY_PATH').text = output
    session.findById('wnd[2]/usr/ctxtDY_FILENAME').text = REDI_NAME
    session.findById('wnd[2]/usr/ctxtDY_FILENAME').caretPosition = 6
    session.findById('wnd[2]/tbar[0]/btn[0]').press()
    session.findById('wnd[1]/tbar[0]/btn[0]').press()
    session.findById('wnd[0]/tbar[0]/btn[15]').press()
    session.findById('wnd[0]/tbar[0]/btn[15]').press()
    
    # Obtén una lista de todas las ventanas abiertas
    all_windows = gw.getWindowsWithTitle('Excel')   

    # Cierra todas las ventanas de Excel    Z
    for window in all_windows:
      window.close()
time.sleep(1)
    
for PEP in UTI_list:
    NAME = PEP.replace("/", "")
    NAME = NAME + ' ' + FECHA + '.xlsx'
    UTI_NAME = 'UTI ' + NAME
    session.findById('wnd[0]/tbar[0]/okcd').text = 'zpsp0008'
    session.findById('wnd[0]').sendVKey(0)
    session.findById('wnd[0]/usr/ctxtP_PSPID').text = PEP
    session.findById('wnd[0]/usr/ctxtP_PSPID').caretPosition = 5
    session.findById('wnd[0]/tbar[1]/btn[8]').press()
    session.findById('wnd[0]/usr/cntlGRID1/shellcont/shell').setCurrentCell(-1, 'AUFNR')
    session.findById('wnd[0]/usr/cntlGRID1/shellcont/shell').selectColumn('AUFNR')
    session.findById('wnd[0]/tbar[1]/btn[28]').press()
    session.findById('wnd[0]/mbar/menu[0]/menu[1]/menu[1]').select()
    session.findById('wnd[1]/usr/ctxtDY_PATH').text = output
    session.findById('wnd[1]/usr/ctxtDY_FILENAME').text = UTI_NAME
    session.findById('wnd[1]/usr/ctxtDY_FILENAME').caretPosition = 4
    session.findById('wnd[1]/tbar[0]/btn[0]').press()
    session.findById('wnd[0]/tbar[0]/btn[15]').press()
    session.findById('wnd[0]/tbar[0]/btn[15]').press()
    time.sleep(1)

    # Obtén una lista de todas las ventanas abiertas
    all_windows = gw.getWindowsWithTitle('Excel')   

    # Cierra todas las ventanas de Excel    Z
    for window in all_windows:
      window.close()
      
# Obtén una lista de todas las ventanas abiertas
all_windows = gw.getWindowsWithTitle('Excel')       
# Cierra todas las ventanas de Excel 
for window in all_windows:
      window.close()
       
# Run SAP Scriptsession = None
connection = None
application = None
SapGuiAuto = None

time.sleep(2)


