import os

from flask import Flask

environment = os.getenv('FLASK_ENV', 'production')

# Flask application
app = Flask(__name__, instance_relative_config=True)

from app import routes

config_type = {
  "development":  "config.DevelopmentConfig",
  "testing": "config.TestingConfig",
  "production": "config.ProductionConfig"
}

app.config.from_object(config_type.get(environment))
app.config.from_pyfile('application.cfg', silent=True)