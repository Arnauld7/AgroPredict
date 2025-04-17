import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    # Modèles paths
    GB_MODEL_DIR = os.path.join(basedir, 'models', 'gradient_boosting')
    TF_MODEL_DIR = os.path.join(basedir, 'models', 'tensorflow')
    # Dataset path
    DATASET_PATH = os.path.join(os.path.dirname(basedir), 'Datasets', 'Crop_recommendation.csv')

class DevelopmentConfig(Config):
    DEBUG = True
    RESTX_MASK_SWAGGER = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    # Configuration de sécurité pour la production
    # Exemple: JWT, CORS, etc.

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)