from flask import Flask
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from app.config import config_by_name

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    limiter.init_app(app)
    
    api = Api(app, 
              version='1.0', 
              title='AgroPredict API',
              description='API pour la recommandation de cultures agricoles',
              doc='/docs')
    
    # Importer les namespaces
    from app.routes.predict import api as predict_ns
    from app.routes.crops import api as crops_ns
    from app.routes.model import api as model_ns
    
    # Ajouter les namespaces à l'API
    api.add_namespace(predict_ns, path='/predict')
    api.add_namespace(crops_ns, path='/crops')
    api.add_namespace(model_ns, path='/model')
    
    return app