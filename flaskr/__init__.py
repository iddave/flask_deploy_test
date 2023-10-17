import os

from flask import Flask, render_template, redirect
from flaskr.filters.custom_filters import map_to_color


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.config['DATABASE_CONNECTION_OPTIONS'] = '-c client_encoding=utf8'
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    app.jinja_env.filters['map_to_color'] = map_to_color

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        return redirect('/test/qaform')

    from . import db
    db.init_app(app)
    # app.register_blueprint('test_form.bp')

    from .qa_form import bp as test_bp
    app.register_blueprint(test_bp)

    return app