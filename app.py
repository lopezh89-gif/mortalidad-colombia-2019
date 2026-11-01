from pathlib import Path
import pandas as pd
import plotly.express as px
from mapa_departamentos import construir_mapa
from dash import Dash, html, dcc, Input, Output, dash_table

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'/'mortalidad_2019_preparada.csv.gz'
df=pd.read_csv(DATA,dtype={'COD_DANE':str,'COD_DEPARTAMENTO':str,'COD_MUERTE':str,'COD3':str},low_memory=False)
df['MES']=pd.to_numeric(df.MES,errors='coerce')
MESES={1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
EDADES=['Mortalidad neonatal','Mortalidad infantil','Primera infancia','Niñez','Adolescencia','Juventud','Adultez temprana','Adultez intermedia','Vejez','Longevidad / Centenarios','Edad desconocida']
COLORS=['#12476a','#2c91a2','#d4a246','#8d77a9']
app=Dash(__name__,title='Mortalidad Colombia 2019')
server=app.server

def card(child, className='card'):
    return html.Section(child, className=className)
def graph(title,id,description):return card([html.H2(title),dcc.Graph(id=id,config={'displaylogo':False}),html.P(description,className='note')])
app.layout=html.Div(className='container',children=[
 html.Header([html.P('OBSERVATORIO INTERACTIVO · FUENTE DANE',className='eyebrow'),html.H1('Mortalidad en Colombia | 2019'),html.P('Análisis territorial, temporal, demográfico y por causas de defunción no fetal.')]),
 card([html.Div([html.Label('Departamento'),dcc.Dropdown(id='departamento',options=[{'label':'Todos los departamentos','value':'ALL'}]+[{'label':x,'value':x} for x in sorted(df.DEPARTAMENTO.dropna().unique())],value='ALL',clearable=False)]),html.Div([html.Label('Sexo'),dcc.Dropdown(id='sexo',options=[{'label':'Todos','value':'ALL'}]+[{'label':x,'value':x} for x in sorted(df.SEXO_LABEL.dropna().unique())],value='ALL',clearable=False)]),html.Div([html.Label('Mes'),dcc.Dropdown(id='mes',options=[{'label':'Todos','value':'ALL'}]+[{'label':MESES[i],'value':i} for i in range(1,13)],value='ALL',clearable=False)])],className='filters'),
 html.Div(id='kpis',className='kpis'),
 html.Div([graph('Distribución de defunciones por departamento','mapa','El tamaño del marcador representa el volumen de defunciones. La posición usa un centroide aproximado construido con los municipios georreferenciados; no es un mapa coroplético.'),graph('Evolución mensual de las defunciones','lineas','Los filtros pueden modificar la serie temporal; para observar la evolución anual completa seleccione «Todos» en mes.')],className='grid'),
 html.Div([graph('Cinco municipios con más casos X95','homicidios','X95: agresión con disparo de otras armas de fuego y no especificadas. No comprende todas las categorías de homicidio.'),graph('Diez municipios con menos defunciones','menor','Son conteos absolutos, NO tasas de mortalidad. La comparación de riesgo requiere población expuesta; los municipios con cero defunciones no aparecen en registros.')],className='grid'),
 card([html.H2('Diez principales causas de muerte (CIE-10, tres caracteres)'),html.Div(id='tabla'),html.P('Cada código de tres caracteres agrupa los subcódigos de cuatro caracteres de la causa básica registrada.',className='note')]),
 html.Div([graph('Defunciones por sexo y departamento','sexo_departamento','Barras apiladas para contrastar la composición de los registros por sexo en cada departamento.'),graph('Defunciones por grupo de edad DANE','edad','Las categorías respetan la correspondencia de códigos GRUPO_EDAD1 establecida en la actividad. Se muestran frecuencias, no una tasa de riesgo por edad.')],className='grid'),
 html.Footer(['Fuente: DANE, defunciones no fetales 2019. Procesamiento propio. | Curso: Aplicaciones I / Actividad de Dash y Plotly · Estudiante: Jonnathan López Hurtado · 2026-II'])
])

@app.callback(Output('kpis','children'),Output('mapa','figure'),Output('lineas','figure'),Output('homicidios','figure'),Output('menor','figure'),Output('tabla','children'),Output('sexo_departamento','figure'),Output('edad','figure'),Input('departamento','value'),Input('sexo','value'),Input('mes','value'))
def actualizar(dep,sexo,mes):
 d=df
 if dep!='ALL':d=d[d.DEPARTAMENTO.eq(dep)]
 if sexo!='ALL':d=d[d.SEXO_LABEL.eq(sexo)]
 if mes!='ALL':d=d[d.MES.eq(mes)]
 total=len(d);locs=d.COD_DANE.nunique();causas=d.COD3.nunique()
 k=[html.Div([html.Small(label),html.Strong(f'{n:,}'.replace(',','.'))],className='kpi') for label,n in [('Defunciones',total),('Municipios registrados',locs),('Causas CIE-10',causas)]]
 mapa = construir_mapa(d)  
 monthly=d.groupby('MES').size().reindex(range(1,13),fill_value=0).reset_index(name='Defunciones');monthly['Mes']=monthly.MES.map(MESES)
 lineas=px.line(monthly,x='Mes',y='Defunciones',markers=True,template='plotly_white',color_discrete_sequence=COLORS)
 hx=d[d.COD3.eq('X95')].groupby(['COD_DANE','MUNICIPIO','DEPARTAMENTO']).size().nlargest(5).reset_index(name='Casos')
 hx['Lugar']=hx.MUNICIPIO+' · '+hx.DEPARTAMENTO
 homicidios=px.bar(hx.sort_values('Casos'),x='Casos',y='Lugar',orientation='h',template='plotly_white',color_discrete_sequence=COLORS)
 municipios=d.groupby(['COD_DANE','MUNICIPIO','DEPARTAMENTO']).size().nsmallest(10).reset_index(name='Defunciones')
 municipios['Lugar']=municipios.MUNICIPIO+' · '+municipios.DEPARTAMENTO
 menor=px.pie(municipios,names='Lugar',values='Defunciones',hole=.32)
 top=d.groupby(['COD3','CAUSA3'],dropna=False).size().nlargest(10).reset_index(name='Total');top=top.rename(columns={'COD3':'Código','CAUSA3':'Causa'})
 tabla=dash_table.DataTable(data=top.fillna('Sin descripción').to_dict('records'),columns=[{'name':v,'id':v} for v in ['Código','Causa','Total']],style_table={'overflowX':'auto'},style_cell={'textAlign':'left','padding':'10px','whiteSpace':'normal','height':'auto'},style_header={'backgroundColor':'#e8f2f5','fontWeight':'bold'},style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'#f7f9fb'}])
 grouped=d.groupby(['DEPARTAMENTO','SEXO_LABEL']).size().reset_index(name='Defunciones')
 sexfig=px.bar(grouped,x='DEPARTAMENTO',y='Defunciones',color='SEXO_LABEL',barmode='stack',template='plotly_white',color_discrete_sequence=COLORS)
 sexfig.update_layout(xaxis_tickangle=-60,legend_title_text='Sexo')
 ages=d.groupby('EDAD_CATEGORIA').size().reindex(EDADES,fill_value=0).reset_index(name='Defunciones')
 ages=ages.rename(columns={'EDAD_CATEGORIA':'Grupo de edad'})
 edad=px.bar(ages,x='Grupo de edad',y='Defunciones',template='plotly_white',color_discrete_sequence=COLORS)
 edad.update_layout(xaxis_tickangle=-40)
 for f in [lineas,homicidios,menor,sexfig,edad]:f.update_layout(margin=dict(t=20,b=35,l=20,r=15),height=400)
 return k,mapa,lineas,homicidios,menor,tabla,sexfig,edad

if __name__=='__main__':app.run(debug=False,host='0.0.0.0',port=8050)
