# /app/dashapp/callbacks.py

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from datetime import datetime, date
from dash.dependencies import Input, Output, State
from psycopg2.extras import RealDictCursor

# Local imports
from task_list.database import get_conn

pio.templates["draft"] = go.layout.Template(
    layout_annotations=[
        dict(
            textangle=-30,
            opacity=0.1,
            font=dict(color="black", size=100),
            xref="paper",
            yref="paper",
            
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ],layout=dict(plot_bgcolor='light gray')
)

color_dict = {'DOWNTOWN SES':"#0000E6",
    '10TH AVE MARINE TERM':'#009543',
    'ALPINE':'#37FDFC',
    'CHICANO PARK':'#DAA520',
    'OCEANVIEW BLVD':'#AA00FF',
    'SAN YSIDRO':'#EA0034'}

pio.templates.default = "draft"

def convert_date(date_string):
    """Converts isoformat date to utctimestamp (seconds from 1970) YYYY-MM-DD"""
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    return int(dt.timestamp())

def get_sensor_time_series_data(id_ls, start_date_, end_date_):
    """Get the time series data in a Pandas DataFrame, for the sensor chosen in the dropdown"""

    sd = convert_date(start_date_)
    ed = convert_date(end_date_) + 60*60*24

    if type(id_ls) == int:
        id_ls = [id_ls]

    sql = f"""SELECT 
                site_data.site_id AS site_id,
                sites.name AS name,
                site_data.time AS time,
                site_data.reading AS reading
            FROM site_data
            LEFT JOIN sites 
                ON site_data.site_id = sites.id
            WHERE site_id in ( {', '.join([str(x) for x in id_ls])} ) AND 
            time > {sd} AND
            time < {ed}
            """

    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [x[0] for x in cursor.description]

    df = pd.DataFrame(rows, columns=columns)
    df['datetime'] = df['time'].apply(lambda x: datetime.fromtimestamp(x))
    
    return df

def get_graph(trace, title):
    """Get a Plotly Graph object for Dash"""

    fig = go.Figure(data=trace, layout=go.Layout( 
                    title=title, 
                    plot_bgcolor='#fbf9f6',
                    height=700,
                    width=1000, 
                    xaxis=dict(
                    autorange=True,
                    type = "date",
                    # Alternative time filter slider
                    rangeslider = dict(
                        visible = True
                    ),
                    )))

    fig.update_layout(legend=dict(
        orientation="h",
        y=-0.43,
        xanchor="right",
        x=1
        ),title={
        'y':0.92,
        'yanchor': 'top',
        'font_size':20},
        yaxis_title={'text':"Hourly Concentrations (&mu;g/m<sup>3</sup>)",
            'font_size':16})
    
    return dcc.Graph(
        # Disable the ModeBar with the Plotly logo and other buttons
        config=dict(
            displayModeBar=False
        ),
        style={'height':'100%'},
        figure=fig
        )


def register_callbacks(dash_app):
    """Register the callback functions for the Dash app, within the Flask app"""        

    @dash_app.callback(
        Output("time_series_chart_col", "children"),
        [Input("types_dropdown", "value"), Input("date_picker", "start_date"),
        Input("date_picker", "end_date")],
    )
    def get_time_series_chart(
        types_dropdown_value, 
        start_date, 
        end_date
    ):
        """Get the sensors available, based on both the location and type of sensor chosen"""
        df = get_sensor_time_series_data(types_dropdown_value, start_date, end_date)

        title = f"San Diego County Black Carbon Concentrations <br>({start_date} through {end_date})"

        scatter_ls = []
        for name in df['name'].unique():
            temp = df[df['name']==name]
            scatter_ls.append(go.Scatter(x=temp['datetime'], y=temp['reading'], name=name, line=dict(color=color_dict[name], width=1)))
        
        graph = get_graph(scatter_ls, title)

        return html.Div(
            [
                dbc.Row(dbc.Col(graph, style={"height": "100%"}))
            ],
            style={'height':'800px'}
        )