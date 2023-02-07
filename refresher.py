import plotly.graph_objects as go
import pandas as pd
import pyodbc as pyo
import time
import streamlit as st

st.set_page_config(
    page_title="PDA online",
    layout="wide",
    initial_sidebar_state = 'collapsed'
)

col1 = st.sidebar
col1.header('Opciones de filtrado')

# Atividad packing
activ = ['EMPAQUE','SELECCION','PESADO']
cult = ['UVA']
#nave = ['NAVE 2 - L1','NAVE 3 - L1']

activ_selection = col1.selectbox('Actividad:', activ)
cult_selection = col1.selectbox('Cultivo:', cult)
#nave_selection = col1.selectbox('Nave:', nave)

server = '10.10.10.5'
db = 'BD_DWH'
tcon = 'yes'
uname = 'JURIBE'
pword = '$DWH2017$'

# Stored Procedure Call Statement
sqlExecSP="{call spsel_PEDATEOReal ()}"

## From SQL to DataFrame Pandas
cnxn = pyo.connect(driver='{SQL Server Native Client 11.0}', 
                      host=server, database=db,
                      user=uname, password=pword)


def read_query(conn, sql) -> pd.DataFrame:
    cursor=conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    df = pd.DataFrame.from_records(rows, columns=[x[0] for x in cursor.description])
    if cursor is not None:
        cursor.close()
    return df

placeholder = st.empty()

def tableproc(tiponave):
    if tiponave == 0: 
        nave = 'NAVE 2 - L1'
    else:
        nave = 'NAVE 3 - L1'
        
    df = read_query(cnxn,sqlExecSP)
    df_PEDATEO = df.groupby(['LINEA', 'CULTIVO', 'DNI', 'NOMBRES', 'ACTIVIDAD'])['CANTIDAD'].sum().reset_index()
    df_EMPAQUEN2 = df_PEDATEO[(df_PEDATEO['LINEA'] == nave) & (df_PEDATEO['ACTIVIDAD'].isin([activ_selection])) & (df_PEDATEO['CULTIVO'].isin([cult_selection]))]
    #df_EMPAQUEN3 = df_PEDATEO[(df_PEDATEO['LINEA']. isin([nave_selection])) & (df_PEDATEO['ACTIVIDAD'].isin([activ_selection])) & (df_PEDATEO['CULTIVO'].isin([activ_selection]))]

    df_EMPAQUEN2.sort_values(by='CANTIDAD',ascending=False, inplace=True)
    df_EMPAQUEfill = df_EMPAQUEN2.loc[:,['ACTIVIDAD','DNI','NOMBRES','CANTIDAD']]

    #placeholder.text("RENDIMIENTO PDA (ONLINE)")
    # Draw a table
    rowEvenColor = '#2F4F4F'
    rowOddColor = '#0F0D42'
    fig = go.Figure()
    fig.add_trace( 
        go.Table(
            #columnorder = [3,4,6],
            # ['<b>LINEA<b>', '<b>CULTIVO<b>','<b>DNI<b>','<b>NOMBRES<b>','<b>ACTIVIDAD<b>','<b>CANTIDAD<b>']
            columnwidth = [40,120],
            header = dict(values=list(['<b>ACTIVIDAD<b>','<b>DNI<b>','<b>NOMBRES<b>','<b>CANTIDAD<b>']),
                        line_color='#f3c92b',
                        fill_color='#f3c92b',
                        align=['left','center'],
                        font=dict(color='#0F0D42', size=16),
                        height=35),
            cells = dict(values=[df_EMPAQUEfill.iloc[:,num] for num in range(len(df_EMPAQUEfill.columns))],
                        line_color='darkslategray',
                        fill_color = [[rowOddColor,rowEvenColor]*40],
                        align=['center', 'center'],
                        font=dict(color='#f3c92b', size=16),
                        height=30)
        )
    )
    fig.update_layout(
        title=go.layout.Title(
        text="RENDIMIENTO "+nave+" / "+activ_selection+" / "+cult_selection+"<br>"+"<sup>"+"PDA ONLINE"+"</sup>"),
        autosize=False,
        width=1200,
        height=730,
            legend=dict(
                title=None, orientation="v", y=1, x=1, 
                font=dict(
                    family="Segoe UI Symbol",
                    size=11.5,
                    color="black"
                    ),
                borderwidth=0
                )
            )
    placeholder.plotly_chart(fig)


#st.markdown(f'*Available Result: {number_of_result}*')
def page2():
    tableproc(0)
    # placeholder.text("Hello p2")
    # placeholder.markdown("# Page 2 ❄️")
    # placeholder.dataframe(df_EMPAQUEN2.sort_values(by=['CANTIDAD'], ascending=False))

def page3():
    tableproc(1)
    # placeholder.text("Hello p3")
    # placeholder.markdown("# Page 3 ❄️")
    #placeholder.dataframe(df_EMPAQUEN3.sort_values(by=['CANTIDAD'], ascending=False))


page_names_to_funcs = {
    "Page 2": page2,
    "Page 3": page3,
}


def refresher(seconds):
    while True:
        page_names_to_funcs["Page 2"]()
        time.sleep(seconds)
        ###################
        page_names_to_funcs["Page 3"]()
        time.sleep(seconds)
        ###################

    
while(1):
    refresher(5)


        # mainDir = os.path.dirname(__file__)
        # filePath = os.path.join(mainDir, 'dummy.py')
        # with open(filePath, 'w') as f:
        #     f.write(f'# {st.write(randint(0, 10000))}')
        # time.sleep(seconds)
