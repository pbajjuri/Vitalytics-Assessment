from dash import Dash, html, dash_table, dcc, Input, Output, callback
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

##******************************** Data Pre-processing ********************************
df = pd.read_excel("./data/SV.xlsx")
df.dropna()
data_cols = ['Filters','Institutions','Very favorable', 'Somewhat favorable', 'Somewhat unfavorable',
       'Very unfavorable', 'Heard Of, No Opinion', 'Never Heard Of']
viewable_cols = data_cols[1:]
df = df[data_cols]

filter_labels = {'Education': 'Educ: ', 'Age': 'Age: ', 'Income': 'Income: '}
filtered_data = False
filter_options = {}
for k,v in filter_labels.items():
    filtered_data = filtered_data | df['Filters'].str.startswith(v)
    filter_options[k] = [x[len(v):] for x in df[df['Filters'].str.startswith(v)]['Filters'].unique() ]
filter_options['Institution'] = [x for x in sorted(df['Institutions'].unique())]
filtered_data = df[filtered_data]

viewable_data = filtered_data[viewable_cols]


##******************************** App *****************************
app.layout = dbc.Container([
    dcc.Markdown('# Do you have a favorable or unfavorable opinion of each of the following Institutions?', style={'textAlign':'center'}),

    dbc.Row([
            dbc.Col(html.Label('Institution',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 3, className = 'ps-4'),
            dbc.Col(html.Label('Education',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 3, className = 'ps-4'),
            dbc.Col(html.Label('Age',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 3, className = 'ps-4'),
            dbc.Col(html.Label('Income',style={'font-weight': 'bold', "text-align": "start", 'font-size': 25}), width = 3, className = 'ps-4'),
        ], justify = 'start'),
    dbc.Row([
        dbc.Col([
            insti_drop := dcc.Dropdown(options=filter_options['Institution'])
        ], width=3),
        dbc.Col([
            edu_drop := dcc.Dropdown(options=filter_options['Education'])
        ], width=3),
        dbc.Col([
            age_drop := dcc.Dropdown(options=filter_options['Age'])
        ], width=3),
        dbc.Col([
            income_drop := dcc.Dropdown(options=filter_options['Income'])
        ], width=3),

    ], justify="between", className='mt-3 mb-4'),

    dbc.Label("Show number of rows"),
    row_drop := dcc.Dropdown(value=10, clearable=False, style={'width':'35%'},
                             options=[10, 25, 50, 100]),

    my_table := dash_table.DataTable(
        columns= [{'id': i, 'name': i} for i in viewable_data.columns[:1]] +
          [{'id': i, 'name': i, 'type': 'numeric', 'format': dash_table.FormatTemplate.percentage(2)} for i in viewable_data.columns[1:]],
        data=viewable_data.to_dict('records'),
        filter_action='native',
        page_size=10,

        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'backgroundColor': 'rgb(232, 241, 254)',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(239, 246, 254)',
            }
        ],
        style_header={
            'backgroundColor': 'grey',
            'color': 'white',
            'fontWeight': 'bold'
        },

    ),
    
])

@callback(
    Output(my_table, 'data'),
    Output(my_table, 'page_size'),
    Input(insti_drop, 'value'),
    Input(edu_drop, 'value'),
    Input(age_drop, 'value'),
    Input(income_drop, 'value'),
    Input(row_drop, 'value')
)
def filter_view(insti_v, edu_v, age_v, income_v, row_v):
    dff = filtered_data.copy()
    filter_cond = False
    no_filter = True
    if insti_v:
        dff = dff[dff['Institutions']==insti_v]
    
    if edu_v:
        filter_cond = filter_cond | dff['Filters'].str.startswith(filter_labels['Education']+edu_v)
        no_filter = False
    
    if age_v:
        filter_cond = filter_cond | dff['Filters'].str.startswith(filter_labels['Age']+age_v)
        no_filter = False
    
    if income_v:
        filter_cond = filter_cond | dff['Filters'].str.startswith(filter_labels['Income']+income_v)
        no_filter = False

    if no_filter == False:
        dff = dff[filter_cond]
    
    return dff.to_dict('records'), row_v


if __name__ == "__main__":
    app.run_server(debug=True, port=8002)