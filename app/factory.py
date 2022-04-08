import logging

from flask import Flask
from app.measurement.views import initConnection
from app.config import DevConfig, BaseConfig
root_path = None


def create_app(config=BaseConfig):
    global root_path
    """
    Factory pattern; create new app with specified config
    :param config: configuration object
    :return: app object
    """

    # new app object
    app = Flask('manage')

    # configure app
    root_path = app.root_path
    app.config.from_object(config)

    # load blueprints
    load_blueprints(app)

    # Logging levels
    # CRITICAL 50
    # ERROR 40
    # WARNING 30
    # INFO 20
    # DEBUG 10
    # NOTSET 0

    logging.basicConfig(filename=app.root_path + '/logs/app.log', level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s: %(message)s')
    logging.info("[i] App initialized")

    initConnection()

    return app

def load_blueprints(app):
    """
    Load all blueprints
    :param app: app in which blueprints are registered
    :return:
    """

    from .measurement.views import measurement_bp
    from .data.views import data_bp

    # register blueprints
    app.register_blueprint(measurement_bp)
    app.register_blueprint(data_bp)
