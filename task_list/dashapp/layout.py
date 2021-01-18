# https://www.sandiegocounty.gov/content/sdc/apcd/en/CurrentAirQuality.html

# /app/dashapp/layout.py

import os

from datetime import date
from flask import url_for
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import psycopg2
from psycopg2.extras import RealDictCursor

# Local imports
from task_list.database import get_conn


def get_navbar():
    """Get a Bootstrap 4 navigation bar for our single-page application's HTML layout"""

    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Data Source", href="https://www.sandiegocounty.gov/content/sdc/apcd/en/CurrentAirQuality.html")),
            dbc.NavItem(dbc.NavLink("EPA Black Carbon Info", href="https://www.epa.gov/sites/production/files/2013-12/documents/black-carbon-fact-sheet_0.pdf")),
        ],
        brand="Home",
        brand_href="/",
        color="dark",
        dark=True,
    )


def get_sensor_types():
    """Get a list of different types of sensors"""
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            name as label, 
            id as value
        FROM sites;
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        # types is a list of dictionaries that looks like this, for example:
        # [{'label': 'a', 'value': 'a'}]
        types = cursor.fetchall()
    
    return types

def get_body():
    """Get the body of the layout for our Dash SPA"""

    types = get_sensor_types()

    # The layout starts with a Bootstrap row, containing a Bootstrap column
    return dbc.Row(
        [
            # 1st column and dropdown (NOT empty at first)
            dbc.Col(
                [
                    html.Label('Location of Sensors', style={'margin-top': '1.5em'}),
                    dcc.Dropdown(
                        options=types,
                        value=types[0]['value'],
                        id="types_dropdown",
                        multi=True
                        # multi=True
                    )
                ], xs=12, sm=6, md=4
            ),
            # 2nd column and dropdown (empty at first)
            dbc.Col(
                [
                    html.Label('Date Selector', style={'margin-top': '1.5em'}),
                    dcc.DatePickerRange(
                        # options=None,
                        # value=None,
                        id="date_picker",
                        min_date_allowed=date(2019, 10, 1),
                        max_date_allowed=date(2021, 1, 31),
                        initial_visible_month=date(2020, 12, 1))

                ], xs=12, sm=6, md=4
            )
        ]
    )

def get_chart_row(): # NEW
    """Create a row and column for our Plotly/Dash time series chart"""

    return dbc.Row(
        dbc.Col(
            id="time_series_chart_col"
        )
    )

def get_layout():
    """Function to get Dash's "HTML" layout"""

    # A Bootstrap 4 container holds the rest of the layout
    return dbc.Container(
        [
            get_navbar(),
            get_body(),
            get_chart_row(),
        ], 
    )