import streamlit as st
import pandas as pd
import plotly.graph_objects as go

ruta = 'https://github.com/juliandariogiraldoocampo/analisis_taltech/raw/refs/heads/main/explorador/Estado_de_la_prestaci%C3%B3n_del_servicio_de_energ%C3%ADa_en_Zonas_No_Interconectadas_20251021.csv'
df = pd.read_csv(ruta)

df['ENERGÍA REACTIVA'] = df['ENERGÍA REACTIVA'].str.replace(',', '').astype(float).astype(int)
df['ENERGÍA ACTIVA'] = df['ENERGÍA ACTIVA'].str.replace(',', '').astype(float).astype(int)
df['POTENCIA MÁXIMA'] = df['POTENCIA MÁXIMA'].str.replace(',', '').astype(float)

lst_cambio = [['Á','A'],['É','E'], ['Í','I'], ['Ó','O'], ['Ú','U']]

# Realizar los reemplazos en las columnas 'DEPARTAMENTO' y 'MUNICIPIO'
for i in range(5):
    df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.replace(lst_cambio[i][0],lst_cambio[i][1])
    df['MUNICIPIO'] = df['MUNICIPIO'].str.replace(lst_cambio[i][0],lst_cambio[i][1])

# Crear una condición negativa para filtrar los departamentos no deseados
condicion_filtro = ~df['DEPARTAMENTO'].isin([
'ARCHIPIELAGO DE SAN ANDRES',
'ARCHIPIELAGO DE SAN ANDRES y PROVIDENCIA',
'ARCHIPIELAGO DE SAN ANDRES, PROVIDENCIA Y SANTA CATALINA'
])
df_colombia_continental = df[condicion_filtro]
df_agrupado = df_colombia_continental.groupby(['DEPARTAMENTO', 'MUNICIPIO'])[['ENERGÍA ACTIVA', 'ENERGÍA REACTIVA']].sum().reset_index()

df_pivote = df_colombia_continental.pivot_table(
    index = 'DEPARTAMENTO',
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
)

# Cálculo de Total por departamento y Año de Energía Activa
df_activa = df_colombia_continental.pivot_table(
    columns = 'AÑO SERVICIO',
    values = ['ENERGÍA ACTIVA'],
    aggfunc = 'sum'
).reset_index(drop=True)

filas = df.shape[0]
columnas = df.shape[1]

df_depto_anos=df_colombia_continental.groupby(['DEPARTAMENTO','AÑO SERVICIO'])['ENERGÍA ACTIVA'].sum().reset_index()
departamentos=df_depto_anos['DEPARTAMENTO'].unique().tolist()



tot_ac_25 = df_activa[2025].to_list()[0]
tot_ac_24 = df_activa[2024].to_list()[0]
tot_ac_23 = df_activa[2023].to_list()[0]
tot_ac_22 = df_activa[2022].to_list()[0]
tot_ac_21 = df_activa[2021].to_list()[0]

delta_25 = (tot_ac_25 - tot_ac_24)/tot_ac_24*100  
delta_24 = (tot_ac_24 - tot_ac_23)/tot_ac_23*100  
delta_23 = (tot_ac_23 - tot_ac_22)/tot_ac_22*100  
delta_22 = (tot_ac_22 - tot_ac_21)/tot_ac_21*100  

######################## VISUALIZACION EN STREAMLIT
st.set_page_config(
    page_title='Zonas No Interconectadas',
    layout='centered')

st.markdown(
    '''
    <style>
        .block-container {
        max-width: 900px;
        }

    ''',
    unsafe_allow_html=True
)


# st.title('Dashboard Zonas No Interconectadas')
# st.header('Análisis de datos')
# st.subheader('Bootcamp Talento Tech')
st.image('img/encabezado.png')
st.html('<b>Tamaño del Conjunto de Datos</b>')
col1,col2 = st.columns(2)
with col1:
    st.markdown(
        f'''
        <h3 style =
        'color: #CC5500;
        background: #CC550055;
        border: 2px solid #CC5500;
        border-radius: 10px;
        margin: 20px;
        padding: 10px;
        text-align: center'> 
        Número de filas<br>:{filas}
        </h3>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(
        f'''
        <h3 style =
        'color: #CC5500;
        background: #CC550055;
        border: 2px solid #CC5500;
        border-radius: 10px;
        margin: 20px;
        padding: 10px;
        text-align: center'> 
        Número de Columnas<br>:{columnas}
        </h3>
        ''',
        unsafe_allow_html=True
    )

with col2:
    with st.expander('Ver conjunto de datos completo'):
        st.dataframe(df)

    with st.expander('Ver Datos de Energía Activa por Departamento y Año'):
        st.dataframe(df_pivote)

#-----------------GRAFICO INTERACTIVO ---------------------------------------------
with st.container(border=True):
    depto_select=st.selectbox(
        'Seleciona un departamento',
        options=departamentos
    )
    condicion_filtro=df_depto_anos['DEPARTAMENTO']==depto_select
    df_departamento=df_depto_anos[condicion_filtro]

    fig_barras=go.Figure()
    fig_barras.add_trace(
        go.Bar(
            x=df_departamento['ENERGÍA ACTIVA'],
            y=df_departamento['AÑO SERVICIO'].astype(str),
            orientation='h',
            marker_color="#CC5500",
            text=df_departamento['ENERGÍA ACTIVA'],
            texttemplate='%{text:,.0f}',
            textposition='auto',
        )
    )
    fig_barras.update_layout(
        height=400,
        xaxis_title='ENERGÍA ACTIVA KWh',
        yaxis_title='AÑO',
        showlegend=False,
        yaxis={'categoryorder':'category ascending'}
    )
    st.plotly_chart(fig_barras,use_container_width=True)



#------------------------INDICADORES--------------


st.subheader('Indicadores de Energía Activa por año en Millones de kWh')
col3, col4, col5, col6 = st.columns(4)
col3.metric(
    label='2022',
    value= round(tot_ac_22/1000000,2),
    delta= f'{round(delta_22,2)}%',
    help='Este es un valor de ejemplo',
    border=True
)

col4.metric(
    label='2023',
    value= round(tot_ac_23/1000000,2),
    delta= f'{round(delta_23,2)}%',
    border=True
)

col5.metric(
    label='2024',
    value= round(tot_ac_24/1000000,2),
    delta= f'{round(delta_24,2)}%',
    border=True
)

col6.metric(
    label='2025',
    value= round(tot_ac_25/1000000,2),
    delta= f'{round(delta_25,2)}%',
    border=True
)

with st.container(border=True):
    df_activa=df_activa[[2022,2023,2024,2025]].T

    fig = go.Figure()  #Creamos el grafico
    fig.add_trace(
        go.Scatter(
            x=df_activa.index,
            y=df_activa[0],
            mode='lines+markers',
            line=dict(color="#CC5500")
        )
    )

    st.caption('**Fuente datos abiertos gobierno nacional**')
    st.plotly_chart(fig)