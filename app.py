import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


df = pd.read_csv("data/c_presupuestario.csv")

# # Si estas columnas que especifican la etiqueta y el centro están vacías, descartarlas:
# df = df.dropna(subset=['Dimensión valor', 'Cuenta'])

# df = df.drop(columns=['Unnamed: 6', 'Unnamed: 7'])

# def calcular_porcentaje_desviacion(df):
#     df['Porcentaje de desviación'] = ((df['Imp. real'] - df['Imp. presupuestado']) / df['Imp. presupuestado']) * 100
#     df.loc[df['Imp. presupuestado'] == 0, 'Porcentaje de desviación'] = float('NaN')  # Reemplazar por NaN si el importe presupuestado es cero
#     return df

# df = calcular_porcentaje_desviacion(df)


# # Se identifican los valores únicos de la columna "Dimensión valor" y "Cuenta"

def asignar_ids(df, columna_referencia, nombre_variable=None):
    valores_unicos = df[columna_referencia].unique()
    mapeo = {valor: indice for indice, valor in enumerate(valores_unicos, start=1)}
    nombre_nueva_columna = 'ID_' + columna_referencia
    df[nombre_nueva_columna] = df[columna_referencia].map(mapeo)
    
    if nombre_variable:
        globals()[nombre_variable] = mapeo
    
    return df, mapeo

# Función para extraer las cuentas que estén asociadas a dimensión valor:
def obtener_cuentas_asociadas(df, dict_dimension_valor, opcion_centro):
    id_seleccionado_dimension_valor = dict_dimension_valor[opcion_centro]
    df_filtrado_por_dimension_valor = df[df['ID_Dimensión valor'] == id_seleccionado_dimension_valor]
    cuentas_asociadas = df_filtrado_por_dimension_valor['Cuenta'].unique()
    return cuentas_asociadas

# Se instancian las funciones con dichas columnas, a la vez de que se asigna el nombre de cada variable de dict en la misma:
df, dict_dimension_valor = asignar_ids(df, 'Dimensión valor', 'dict_dimension_valor')
df, dict_cuenta = asignar_ids(df, 'Cuenta', 'dict_cuenta')

# Calcular porcentaje de desvío se ejecuta dentro de sumar_valores:
def sumar_valores(df, dict_dimension_valor, opcion_centro, columna):
    id_dimension_valor = dict_dimension_valor[opcion_centro]
    df_filtrado_por_dimension_valor = df[df['ID_Dimensión valor'] == id_dimension_valor]
    suma_valor = df_filtrado_por_dimension_valor[columna].sum()

    return suma_valor

def mostrar_sumas(df, dict_dimension_valor, opcion_centro):
    suma_presupuestado = sumar_valores(df, dict_dimension_valor, opcion_centro, 'Imp. presupuestado')
    suma_real = sumar_valores(df, dict_dimension_valor, opcion_centro, 'Imp. real')
    desvio = suma_real - suma_presupuestado

    st.write("Suma del impuesto presupuestado:", suma_presupuestado)
    st.write("Suma del impuesto real:", suma_real)
    st.write("Desvío:", desvio)

def widget_detalles(df, dict_dimension_valor):
    st.header("Detalles")

    # Seleccionar el año
    df['Año - mes'] = pd.to_datetime(df['Año - mes'])
    años_unicos = df['Año - mes'].dt.year.unique()
    año_seleccionado = st.selectbox('Selecciona un año', options=[*años_unicos, 'Todos los años'])

    # Filtrar por año si no se elige "Todos los años"
    if año_seleccionado != 'Todos los años':
        df_año_seleccionado = df[df['Año - mes'].dt.year == año_seleccionado]
    else:
        df_año_seleccionado = df.copy()  # No aplicar ningún filtro si se seleccionan todos los años

    # Seleccionar el mes basado en el año seleccionado
    meses_disponibles = df['Año - mes'].dt.month_name().unique()
    mes_seleccionado = st.selectbox('Selecciona un mes', options=[*meses_disponibles, 'Todos los meses'])

    # Filtrar por mes si no se elige "Todos los meses"
    if mes_seleccionado != 'Todos los meses':
        df_mes_seleccionado = df_año_seleccionado[df_año_seleccionado['Año - mes'].dt.month_name() == mes_seleccionado]
    else:
        df_mes_seleccionado = df_año_seleccionado.copy()  # No aplicar ningún filtro si se seleccionan todos los meses

    # Seleccionar la dimensión valor basada en el año y mes seleccionados
    ids_dimensión_mes = df_mes_seleccionado['ID_Dimensión valor'].unique()
    df_valores_dimensión_mes = df_mes_seleccionado[df_mes_seleccionado['ID_Dimensión valor'].isin(ids_dimensión_mes)]
    st.write("Actividad de los Centros en este mes:")
    st.write(df_valores_dimensión_mes)

    # Seleccionar el centro basado en el año, mes y dimensión valor seleccionados
    opcion_centro = st.selectbox('Selecciona el Centro', options=[*list(dict_dimension_valor.keys()), 'Todos los centros'])
    if opcion_centro != 'Todos los centros':
        df_filtrado = df_valores_dimensión_mes[df_valores_dimensión_mes['Dimensión valor'] == opcion_centro]
        mostrar_sumas(df_filtrado, dict_dimension_valor, opcion_centro)

        # Seleccionar la cuenta basada en el año, mes, dimensión valor y centro seleccionados
        cuentas_asociadas = obtener_cuentas_asociadas(df, dict_dimension_valor, opcion_centro)
        if len(cuentas_asociadas) > 0:
            opcion_cuenta = st.selectbox('Selecciona la Cuenta', options=[*list(cuentas_asociadas), 'Todas las cuentas'])
            if opcion_cuenta != 'Todas las cuentas':
                id_seleccionado_cuenta = dict_cuenta[opcion_cuenta]
                id_seleccionado_dimension_valor = dict_dimension_valor[opcion_centro]
                df_filtrado = df_filtrado[(df_filtrado['ID_Cuenta'] == id_seleccionado_cuenta) & (df_filtrado['ID_Dimensión valor'] == id_seleccionado_dimension_valor)]
    else:
        # Mostrar todas las cuentas independientemente del centro seleccionado
        cuentas_asociadas = df_valores_dimensión_mes['Cuenta'].unique()
        opcion_cuenta = st.selectbox('Selecciona la Cuenta', options=[*list(cuentas_asociadas), 'Todas las cuentas'])
        if opcion_cuenta != 'Todas las cuentas':
            id_seleccionado_cuenta = dict_cuenta[opcion_cuenta]
            df_filtrado = df_valores_dimensión_mes[df_valores_dimensión_mes['ID_Cuenta'] == id_seleccionado_cuenta]        

    st.write(df_filtrado)


def widget_cashflow():
    st.header("Widget Opción 2")

def widget_cuadro():
    st.header("Widget Opción 3")

def widget_graficos(df):
    st.header("Gráficos")

    # Crear la aplicación Streamlit
    st.title('Análisis de Datos de Ingreso y Egreso por Centro y Tipo de Cuenta')

    # Gráfico de barras para visualizar ingresos y egresos por centro
    st.write('**Ingresos y Egresos por Centro:**')
    ingresos_por_centro = df.groupby('Dimensión valor')['Imp. real'].sum()
    egresos_por_centro = df.groupby('Dimensión valor')['Desvio'].sum()

    fig, ax = plt.subplots()
    ingresos_por_centro.plot(kind='bar', color='blue', alpha=0.5, ax=ax, label='Ingresos')
    egresos_por_centro.plot(kind='bar', color='red', alpha=0.5, ax=ax, label='Egresos')
    ax.set_ylabel('Cantidad')
    ax.set_xlabel('Centro')
    ax.set_title('Ingresos y Egresos por Centro')
    ax.legend()
    st.pyplot(fig)
    fig, ax = plt.subplots(figsize=(10, 6))

    # Graficar la evolución del Imp. real y el Imp. presupuestado a lo largo del tiempo
    df.groupby('Año - mes')['Imp. real'].sum().plot(ax=ax, label='Imp. real', marker='o')
    df.groupby('Año - mes')['Imp. presupuestado'].sum().plot(ax=ax, label='Imp. presupuestado', marker='o')

    # Añadir etiquetas y título
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Monto ($)')  # Etiqueta más apropiada para valores monetarios
    ax.set_title('Evolución de Imp. real e Imp. presupuestado')
    ax.legend()

    # Rotar las etiquetas del eje x para mejor legibilidad
    plt.xticks(rotation=45)

    # Ajustar la escala del eje y
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='plain', useOffset=False)

    # Mostrar el gráfico
    st.pyplot(fig)
    # Tomar el valor absoluto de los ingresos y egresos totales por centro
    ingresos_por_centro_abs = df.groupby('Dimensión valor')['Imp. real'].sum().abs()
    egresos_por_centro_abs = df.groupby('Dimensión valor')['Desvio'].sum().abs()

    # Filtrar los centros con mayores ingresos y egresos
    centros_mayor_ingreso = ingresos_por_centro_abs.nlargest(15)  # Por ejemplo, los 15 centros con mayores ingresos
    centros_mayor_egreso = egresos_por_centro_abs.nlargest(15)  # Por ejemplo, los 15 centros con mayores egresos

    # Crear una figura con dos subgráficos
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(30, 15))

    # Gráfico de pastel para los centros con mayores ingresos
    autotexts1 = ax1.pie(centros_mayor_ingreso, autopct='%1.1f%%', textprops={'fontsize': 10})[1]
    ax1.set_title('Centros con Mayor Ingreso', fontsize=20)
    ax1.legend(centros_mayor_ingreso.index, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Gráfico de pastel para los centros con mayores egresos
    autotexts2 = ax2.pie(centros_mayor_egreso, autopct='%1.1f%%', textprops={'fontsize': 10})[1]
    ax2.set_title('Centros con Mayor Egreso', fontsize=20)
    ax2.legend(centros_mayor_egreso.index, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Mostrar los gráficos
    st.pyplot(fig)



# Barra lateral con opciones
opciones = {
    "Detalles": widget_detalles,
    "Cashflow": widget_cashflow,
    "Cuadro Integral": widget_cuadro,
    "Gráficos": widget_graficos
}



# Mostrar el widget seleccionado
st.sidebar.title("Datos")
opcion_seleccionada = st.sidebar.radio("Selecciona que datos quieres visualizar", list(opciones.keys()))
if opcion_seleccionada == "Detalles":
    widget_detalles(df, dict_dimension_valor)
else:
    widget_funcion = opciones[opcion_seleccionada]
    widget_funcion(df)
