import os
import logging

from flask import Flask, render_template

# Local imports 
from task_list import database
from task_list.dash_setup import register_dashapps


def create_app():
    """Factory function that creates the Flask app"""

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    logging.basicConfig(level=logging.DEBUG)

    @app.route('/')
    def home():
        """non-Dash route"""
        return render_template('index.html')
    
    database.init_app(app) # postgreSQL db with psycopg2

    # for the dash app
    register_dashapps(app)

    return app

