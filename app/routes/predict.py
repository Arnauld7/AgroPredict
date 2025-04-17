from flask import request
from flask_restx import Namespace, Resource, fields
from app.services.predictor import get_predictor
from app import limiter
from app.utils.validators import validate_crop_params

api = Namespace('predict', description='Prédiction de cultures agricoles')

# Définition des modèles pour la documentation
input_model = api.model('InputParameters', {
    'N': fields.Float(required=True, description='Niveau d\'azote dans le sol'),
    'P': fields.Float(required=True, description='Niveau de phosphore dans le sol'),
    'K': fields.Float(required=True, description='Niveau de potassium dans le sol'),
    'temperature': fields.Float(required=True, description='Température en degrés Celsius'),
    'humidity': fields.Float(required=True, description='Humidité relative en %'),
    'ph': fields.Float(required=True, description='pH du sol'),
    'rainfall': fields.Float(required=True, description='Précipitations en mm'),
    'model_type': fields.String(required=False, enum=['gradient_boosting', 'tensorflow', 'tensorflow_lite'], 
                            description='Type de modèle à utiliser (défaut: gradient_boosting)')
})

prediction_model = api.model('PredictionResult', {
    'crop': fields.String(description='Culture recommandée'),
    'confidence': fields.Float(description='Niveau de confiance (0-1)'),
    'model_used': fields.String(description='Modèle utilisé pour la prédiction'),
    'input_parameters': fields.Raw(description='Paramètres d\'entrée utilisés')
})

@api.route('')
class PredictCrop(Resource):
    @api.doc('predict_crop')
    @api.expect(input_model)
    @api.marshal_with(prediction_model, code=200)
    @limiter.limit("10 per minute")
    def post(self):
        """Prédit la culture optimale en fonction des paramètres du sol et du climat"""
        data = request.json
        
        # Validation des paramètres
        errors = validate_crop_params(data)
        if errors:
            api.abort(400, errors)
        
        # Extraction des paramètres
        N = data.get('N')
        P = data.get('P')
        K = data.get('K')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        ph = data.get('ph')
        rainfall = data.get('rainfall')
        model_type = data.get('model_type', 'gradient_boosting')
        
        try:
            # Obtenir l'instance du prédicteur
            predictor = get_predictor()
            
            # Faire la prédiction
            crop, confidence = predictor.predict_crop(
                N, P, K, temperature, humidity, ph, rainfall, model_type)
            
            return {
                'crop': crop,
                'confidence': float(confidence),
                'model_used': model_type,
                'input_parameters': {
                    'N': N,
                    'P': P,
                    'K': K,
                    'temperature': temperature,
                    'humidity': humidity,
                    'ph': ph,
                    'rainfall': rainfall
                }
            }
        except Exception as e:
            api.abort(500, f"Erreur lors de la prédiction: {str(e)}")

@api.route('/simple')
class SimplePredictCrop(Resource):
    @api.doc('predict_crop_get', params={
        'N': {'description': 'Niveau d\'azote', 'type': 'float', 'required': True},
        'P': {'description': 'Niveau de phosphore', 'type': 'float', 'required': True},
        'K': {'description': 'Niveau de potassium', 'type': 'float', 'required': True},
        'temperature': {'description': 'Température (°C)', 'type': 'float', 'required': True},
        'humidity': {'description': 'Humidité (%)', 'type': 'float', 'required': True},
        'ph': {'description': 'pH du sol', 'type': 'float', 'required': True},
        'rainfall': {'description': 'Précipitations (mm)', 'type': 'float', 'required': True},
        'model_type': {'description': 'Type de modèle', 'type': 'string', 'enum': ['gradient_boosting', 'tensorflow', 'tensorflow_lite'], 'default': 'gradient_boosting'}
    })
    @api.marshal_with(prediction_model, code=200)
    @limiter.limit("10 per minute")
    def get(self):
        """Version simplifiée de l'API de prédiction utilisant une méthode GET avec paramètres"""
        try:
            # Vérifier que tous les paramètres requis sont présents
            required_params = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            missing_params = [param for param in required_params if param not in request.args]
            
            if missing_params:
                api.abort(400, f"Paramètres manquants: {', '.join(missing_params)}")
            
            # Extraction des paramètres
            try:
                N = float(request.args.get('N'))
                P = float(request.args.get('P'))
                K = float(request.args.get('K'))
                temperature = float(request.args.get('temperature'))
                humidity = float(request.args.get('humidity'))
                ph = float(request.args.get('ph'))
                rainfall = float(request.args.get('rainfall'))
                model_type = request.args.get('model_type', 'gradient_boosting')
            except (ValueError, TypeError) as e:
                api.abort(400, f"Erreur de conversion: {str(e)}. Tous les paramètres doivent être des nombres.")
            
            # Validation
            data = {
                'N': N, 'P': P, 'K': K, 
                'temperature': temperature, 'humidity': humidity, 
                'ph': ph, 'rainfall': rainfall
            }
            errors = validate_crop_params(data)
            if errors:
                api.abort(400, errors)
            
            # Obtenir l'instance du prédicteur
            predictor = get_predictor()
            
            # Faire la prédiction
            crop, confidence = predictor.predict_crop(
                N, P, K, temperature, humidity, ph, rainfall, model_type)
            
            return {
                'crop': crop,
                'confidence': float(confidence),
                'model_used': model_type,
                'input_parameters': {
                    'N': N,
                    'P': P,
                    'K': K,
                    'temperature': temperature,
                    'humidity': humidity,
                    'ph': ph,
                    'rainfall': rainfall
                }
            }
        except Exception as e:
            api.abort(500, f"Erreur lors de la prédiction: {str(e)}")