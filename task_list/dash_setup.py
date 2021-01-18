# /app/dash_setup.py

import dash
from flask.helpers import get_root_path


def register_dashapps(app):
    """Register dashapps with Flask app."""

    # external CSS stylesheets
    external_stylesheets = [
        'https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css'
    ]
    
    # external JavaScript files
    external_scripts = [
        "https://code.jquery.com/jquery-3.5.1.slim.min.js",
        "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
        "https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.min.js",
    ]

       # To ensure proper rendering and touch zooming for all devices, add the responsive viewport meta tag
    meta_viewport = [{
        "name": "viewport", 
        "content": "width=device-width, initial-scale=1, shrink-to-fit=no"
    }]
    
    dashapp = dash.Dash(
        __name__,
        # This is where the Flask app gets appointed as the server for the Dash app
        server = app,
        url_base_pathname = '/dash/',
        # Separate assets folder in "static_dash" (optional)
        assets_folder = get_root_path(__name__) + '/static_dash/', 
        meta_tags = meta_viewport, 
        external_scripts = external_scripts,
        external_stylesheets = external_stylesheets
    )
    dashapp.title = 'San Diego BC Data'

    # Some of these imports should be inside this function so that other Flask
    # stuff gets loaded first, since some of the below imports reference the other
    # Flask stuff, creating circular references
    from task_list.dashapp.layout import get_layout
    from task_list.dashapp.callbacks import register_callbacks

    with app.app_context():

        # Assign the get_layout function without calling it yet
        dashapp.layout = get_layout

        # Register callbacks
        # Layout must be assigned above, before callbacks
        register_callbacks(dashapp)

    return None