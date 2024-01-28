# -*- coding: utf-8 -*-
"""
ETF_DashBoard
"""
#%%

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

df = pd.read_excel('../df_etf.xlsx', index_col = 0)

df_copy = df.copy()

#%%

# KODEX ETF & Draw Down Function

condition_kodex = [df_copy.columns[i] for i in range(df_copy.shape[1]) if 'KODEX' in df_copy.columns[i]]

df_copy_kodex = df_copy.loc[:,condition_kodex]


'''
# Correalation 구하는 방법
df_copy_kodex_sample = df_copy_kodex.loc[:,['KODEX 200', 'KODEX 200 중소형']].dropna()

corr_result = df_copy_kodex_sample.corr().values[0,1]
'''


def mdd_fn(DF):
    
    df = DF.copy()
    
    def return_fn(df):
        return df.pct_change().fillna(0)
    
    def cum_return_fn(df_return):
        return (1 + df_return).cumprod()
    
    df['Return'] = return_fn(df)
    
    df['CumReturn'] = cum_return_fn(df['Return'])
    
    df['MaxCumReturn'] = df['CumReturn'].cummax()
    
    df['DrawDown'] = round(((df['CumReturn']/df['MaxCumReturn']) - 1)*100,2)
    
    return df

#options 생성
options = [{'label':i, 'value':i} for i in df_copy_kodex.columns]

# app 생성

app = dash.Dash()

app.layout = html.Div([
    html.Br(),
    html.H1('KODEX ETF DashBoard'),
    
    html.Div(id = 'layout1 div title',
             children = [
                html.H3('Select ETF: ', style = {'paddingRight':'30px'}),
                dcc.Dropdown(id = 'etf_col1',
                             options = options,
                             multi = False,
                             value = ['KODEX 200'],
                             style = {'width':'80%'})
            ], style = {'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),
    
    html.Div(id = 'layout1 div date',
             children = [
                html.H3('Select Start Date & End Date'),
                dcc.Input(id = 'startDate1',
                          value = '20180101',
                          style = {'fontSize':10}),
                dcc.Input(id = 'endDate1',
                          value = '20220206',
                          style = {'fontSize':10})
            ]),
    html.Div(id = 'layout1 div button',
             children = [
                 html.Button(id = 'button1',
                             n_clicks = 0,
                             children = 'Submit',
                             style = {'fontSize':10})
                 
            ]),
    
    dcc.Graph(id = 'graph1'),
    dcc.Graph(id = 'graph2'),
    
    html.Div(id = 'layout2 div title',
             children = [
                     html.H3('Select ETF: ', style = {'paddingRight':'30px'}),
                     dcc.Dropdown(id = 'etf_col2',
                                  options = options,
                                  multi = True,
                                  value = ['KODEX 200', 'KODEX 200 중소형'],
                                  style = {'fontSize':10})
            ]),
    
    html.Div(id = 'layout2 div date',
             children = [
                 html.H3('Select Start Date & End Date'),
                 dcc.Input(id = 'startDate2',
                           value = '20180101',
                           style = {'fontSize':10}),
                 dcc.Input(id = 'endDate2',
                           value = '20220206',
                           style = {'fontSize':10})
            ]),
    
    html.Div(id = 'layout2 div button',
             children = [
                 html.Button(id = 'button2',
                             n_clicks = 0,
                             children = 'Submit',
                             style = {'fontSize':10})
                 
            ]),
    
    dcc.Graph(id = 'graph3')

    ])

@app.callback([Output(component_id = 'graph1', component_property = 'figure'),
               Output(component_id = 'graph2', component_property = 'figure')],
              [Input(component_id = 'button1', component_property = 'n_clicks')],
              [State(component_id = 'etf_col1', component_property = 'value'),
               State(component_id = 'startDate1', component_property = 'value'),
               State(component_id = 'endDate1', component_property = 'value')])
def update_graph_layout1(n_clicks, etf_col, start_date, end_date):
    
    start_year = int(start_date[:4])
    start_month = int(start_date[4:6])
    start_day = int(start_date[6:8])
    start = datetime(start_year, start_month, start_day)
    
    end_year = int(end_date[:4])
    end_month = int(end_date[4:6])
    end_day = int(end_date[6:8])
    end = datetime(end_year, end_month, end_day)
    
    df_trace = df_copy_kodex.loc[start:end,[etf_col]].dropna()
    
    start_date_format = '{}Y-{}M-{}D'.format(df_trace.index[0].year, df_trace.index[0].month, df_trace.index[0].day)
    end_date_format = '{}Y-{}M-{}D'.format(df_trace.index[-1].year, df_trace.index[-1].month, df_trace.index[-1].day)
    
    trace1 = go.Scatter(x = df_trace.index, y = df_trace[etf_col], mode = 'lines', name = '{}'.format(etf_col))
    layout1 = go.Layout(title = '{}'.format(etf_col),
                        xaxis = {'title':'{} ~ {}'.format(start_date_format, end_date_format)},
                        yaxis = {'tickformat':','})
    fig1 = go.Figure(data = trace1, layout = layout1)
    fig1.update_layout(template = 'plotly_dark')
    
    df_dd = mdd_fn(DF = df_trace)
    trace2 = go.Scatter(x = df_dd.index, y = df_dd['DrawDown'], mode = 'lines', name = '{} DrawDown'.format(etf_col), fill = 'tonexty')
    layout2 = go.Layout(title = 'DrawDown of {}'.format(etf_col),
                        xaxis = {'title':'{} ~ {}'.format(start_date_format, end_date_format)},
                        yaxis = {'tickformat':','})
    
    fig2 = go.Figure(data = trace2, layout = layout2)
    fig2.update_layout(template = 'plotly_dark')
    
    return fig1, fig2

@app.callback(Output(component_id = 'graph3', component_property = 'figure'),
              [Input(component_id = 'button2', component_property = 'n_clicks')],
              [State(component_id = 'etf_col2', component_property = 'value'),
               State(component_id = 'startDate2', component_property = 'value'),
               State(component_id = 'endDate2', component_property= 'value')])
def update_graph_layout2(n_clicks, etf_col, start_date, end_date):
    start_year = int(start_date[:4])
    start_month = int(start_date[4:6])
    start_day = int(start_date[6:8])
    start = datetime(start_year, start_month, start_day)
    
    end_year = int(end_date[:4])
    end_month = int(end_date[4:6])
    end_day = int(end_date[6:8])
    end = datetime(end_year, end_month, end_day)
    
    df_trace = pd.DataFrame()
    
    for col in etf_col:
        df_trace['{}'.format(col)] = df_copy_kodex.loc[start:end, col]
    
    df_trace = df_trace.dropna()
    
    start_date_format = '{}Y-{}M-{}D'.format(df_trace.index[0].year, df_trace.index[0].month, df_trace.index[0].day)
    end_date_format = '{}Y-{}M-{}D'.format(df_trace.index[-1].year, df_trace.index[-1].month, df_trace.index[-1].day)
    
    trace = go.Scatter(x = df_trace[df_trace.columns[0]],
                       y = df_trace[df_trace.columns[1]],
                       mode = 'markers')
    
    corr_result = round(df_trace.corr().values[0,1],2)
    
    layout = go.Layout(title = '{} & {} Scatter Plot <br><br> Correlation: {}'.format(df_trace.columns[0], df_trace.columns[1], corr_result),
                       xaxis = {'title':'{} ~ {}'.format(start_date_format, end_date_format),
                                'tickformat':','},
                       yaxis = {'tickformat':','} )
    
    fig = go.Figure(data = trace, layout = layout)
    fig.update_layout(template = 'plotly_dark')
    
    return fig

if __name__=='__main__':
    app.run_server()



















