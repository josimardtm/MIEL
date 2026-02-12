# -*- coding: utf-8 -*-
"""
Microrredes Eléctricas
Ejemplo 1

"""

from dss import DSS as dss_engine
import pandas as pd
import plotly.express as px
import plotly.io as pio


# Inicializar el motor de OpenDSS
dss_circuit = dss_engine.ActiveCircuit
dss_text = dss_engine.Text

# Cargar archivo
# Nota: Usa r"ruta/al/archivo" para evitar problemas con backslashes en Windows
dss_text.Command = r'compile "C:\Program Files\OpenDSS\Examples\Manual\Example1.DSS"'

# Ejecutar el flujo de potencia
dss_text.Command = "solve"

# 4. Ver resultados básicos en la consola de Spyder
if dss_circuit.Solution.Converged:
    print("El flujo de potencia converge")
    
    # # Obtener nombres de buses y magnitudes de tensión (pu)
    # buses = dss_circuit.AllBusNames
    # voltages = dss_circuit.AllBusVmagPu
    
    # print("\nResultados de Tensiones (p.u.):")
    # for bus, vol in zip(buses, voltages):
    #     print(f"Bus: {bus} -> Tensión: {vol:.4f} pu")
    
    nombres_nodos = dss_circuit.AllNodeNames
    voltages = dss_circuit.AllBusVmagPu

    print(f"{'Bus':<20} | {'Tensión Fase A (pu)':<20}")
    print("-" * 45)

    # 3. Filtrar por el sufijo '.1' (Fase A)
    for nombre, volt in zip(nombres_nodos, voltages):
        if ".1" in nombre:
            # Limpiamos el nombre para que se vea solo el Bus (quitamos el .1)
            nombre_bus = nombre.split('.')[0]
            print(f"{nombre_bus:<20} | {volt:.4f} pu")
    
else:
    print("La simulación NO convergió.")

# --- Extracción de Datos ---
# Obtenemos nombres de nodos 
node_names = dss_circuit.AllNodeNames

# Crear una lista de diccionarios para organizar los datos
data = []
for name, volt in zip(node_names, voltages):
    bus_name = name.split('.')[0]
    phase = name.split('.')[1] if '.' in name else '1' # Fase por defecto si no hay punto
    data.append({'Bus': bus_name, 'Tensión (pu)': volt, 'Fase': f'Fase {phase}'})

df = pd.DataFrame(data)

# --- Gráfico con Plotly ---
fig = px.scatter(df, 
                 x='Bus', 
                 y='Tensión (pu)', 
                 color='Fase',
                 title='Perfil de Tensiones por Fase en OpenDSS',
                 labels={'Tensión (pu)': 'Voltaje (p.u.)', 'Bus': 'Nombre del Bus'},
                 hover_data=['Bus'],
                 color_discrete_map={'Fase 1': 'red', 'Fase 2': 'green', 'Fase 3': 'blue'})

# Mejorar el diseño
fig.update_layout(template='plotly_white', xaxis_tickangle=-45)
fig.add_hline(y=1.05, line_dash="dash", line_color="orange", annotation_text="Límite Superior")
fig.add_hline(y=0.95, line_dash="dash", line_color="orange", annotation_text="Límite Inferior")

# Mostrar en el navegador o en la ventana de Spyder
pio.renderers.default = "browser"
fig.show()
    
# Extraer corrientes de las líneas
data_currents = []

# Iterar sobre todas las líneas del circuito
i_line = dss_circuit.Lines.First
while i_line > 0:
    line_name = dss_circuit.Lines.Name
    # CurrentMagPhase devuelve las magnitudes de las corrientes por fase
    # El orden suele ser [I1, I2, I3...] dependiendo del número de fases
    currents = dss_circuit.ActiveCktElement.CurrentsMagAng
    num_phases = dss_circuit.ActiveCktElement.NumPhases
    
    # Solo tomamos las magnitudes (los índices pares: 0, 2, 4...) de la entrada (terminal 1)
    for i in range(num_phases):
        mag = currents[i*2]  # La magnitud está en las posiciones pares
        data_currents.append({
            'Línea': line_name,
            'Corriente (A)': mag,
            'Fase': f'Fase {i+1}'
        })
    
    i_line = dss_circuit.Lines.Next

df_i = pd.DataFrame(data_currents)

# Graficar con Plotly
fig_i = px.bar(df_i, 
               x='Línea', 
               y='Corriente (A)', 
               color='Fase',
               barmode='group', # Muestra las barras de las fases una al lado de la otra
               title='Corrientes por Fase en cada Línea',
               labels={'Corriente (A)': 'Amperios (A)', 'Línea': 'Nombre de la Línea'},
               color_discrete_sequence=px.colors.qualitative.Set1)

fig_i.update_layout(template='plotly_white', xaxis_tickangle=-45)

# Mostrar en el navegador
fig_i.show()

#================================
