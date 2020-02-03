# -- ------------------------------------------------------------------------------------ -- #
# -- Proyecto: Describir brevemente el proyecto en general                                -- #
# -- Codigo: RepasoPython.py - describir brevemente el codigo                             -- #
# -- Repositorio: https://github.com/                                                     -- #
# -- Autor: Alejandra Cortes Soto                                                         -- #
# -- ------------------------------------------------------------------------------------ -- #

# -- ------------------------------------------------------------- Importar con funciones -- #
import funciones as fn
import visualizaciones as vs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# -- --------------------------------------------------------- Descargar precios de OANDA -- #
# Este código nos permite descargar los precios según los parámetros que nosotros indiquemos con la ayuda de la herramienta OANDA
# token de OANDA
OA_Ak = 'db61d16ed80a943c9b65769aea7b75e8-dec8e1238889457a886b69e85640efec'
OA_In = "EUR_USD"  # Instrumento
OA_Gn = "D"  # Granularidad de velas
fini = pd.to_datetime("2019-01-06 00:00:00").tz_localize('GMT')  # Fecha inicial
ffin = pd.to_datetime("2019-12-06 00:00:00").tz_localize('GMT')  # Fecha final

df_pe = fn.f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                             p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)

# -- --------------------------------------------------------------- Graficar OHLC plotly -- #

vs_grafica1 = vs.g_velas(p0_de=df_pe.iloc[0:120, :])
vs_grafica1.show()

# -- ------------------------------------------------------------------- Conteno de velas -- #

# -- 0A.1: Hora
df_pe['Hora'] = list(df_pe['TimeStamp'][i].hour for i in range(0, len(df_pe['TimeStamp'])))  # nueva columna de hora
# -- 0A.2: Dia de la semana.
df_pe['Dia'] = list(df_pe['TimeStamp'][i].weekday() for i in range(0, len(df_pe['TimeStamp'])))
# -- CO: Amplitud de velas (close - open).
closes = pd.DataFrame(float(i) for i in df_pe['Close'])
opens = pd.DataFrame(float(i) for i in df_pe['Open'])
df_pe['CO'] = (closes - opens)
# -- ---------------------------------Ejercicios individuales laboratorio 0 -- #
# -- 01: Mes de la vela.
df_pe['Mes'] = pd.DataFrame(i.month for i in df_pe['TimeStamp'])

# -- 02: Sesion de la vela.
# Este código nos permite identificar la sesión a la que pertenece cada vela según a la hora en la que sucedió el movimiento
# Utilizamos el apoyo de la función tuple
condiciones = [(lambda i: i == 22 or i == 23 or i == 0 or i == 1 or i == 2 or i == 3 or i == 4 or i == 5 or i == 6 or
                          i == 7, 'ASIA'),
               (lambda i: i == 8, 'ASIA_EUROPA'),
               (lambda i: i == 9 or i == 10 or i == 11 or i == 12, 'EUROPA'),
               (lambda i: i == 13 or i == 14 or i == 15 or i == 16, 'EUROPA_AMERICA'),
               (lambda i: i == 17 or i == 18 or i == 19 or i == 20 or i == 21, 'AMERICA')]


# Ahora creamos una función que nos permita utilizar la función de tupla con las condiciones establecidas y los datos de la sección hora
def apply_condiciones(i):
    for condicion, reemplazo in condiciones:
        if condicion(i):
            return reemplazo
    return i


# Por último creamos la columna de sesiones y asignamos los datos obtenidos en base a la función creada
df_pe['Sesion'] = list(map(apply_condiciones, df_pe['Hora']))

# -- 03: Amplitud OC esperada de vela para cualquier dia de la semana (Dist de Freq).
df_pe['OC'] = (closes - opens) * 10000
# -- 04: Amplitud HL esperada de vela para cualquier dia de la semana (Dist de Freq).
high = pd.DataFrame(float(i) for i in df_pe['High'])
low = pd.DataFrame(float(i) for i in df_pe['Low'])
df_pe['HL'] = (high - low) * 10000
# -- 05: Sentido de la vela (Alcista o Bajista)
sentido = (lambda opens, closes: 'ALCISTA' if closes >= opens else 'BAJISTA')
df_pe['Sentido'] = pd.DataFrame(sentido(df_pe['Open'][i], df_pe['Close'][i]) for i in range(len(df_pe['Open'])))

# -- 07: Ventanas móviles de volatilidad
# En este caso utilizamos la función rolling que nos permite elegir una ventana móvil con cierto número de muestras para posteriormente
# aplicar alguna medida estadística, en este caso utilizamos la función max para obtener el máximo valor de la ventana móvil indicada
df_pe['volatilidad_5'] = (df_pe['HL'].rolling(5).max())
df_pe['volatilidad_25'] = (df_pe['HL'].rolling(25).max())
df_pe['volatilidad_50'] = (df_pe['HL'].rolling(50).max())

# -- 08: Gráfica con Plotly
c = df_pe.groupby(['Dia'])['volatilidad_5'].mean()
fig = px.scatter(x=[0, 1, 2, 3, 4, 6], y=c, labels={'x': 'Dia de la semana', 'y': 'Promedio volatilidad (5)'},
                 title='Volatilidad en los días de la semana')
fig.show()
