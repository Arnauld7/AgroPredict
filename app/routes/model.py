from flask import send_file, current_app
from flask_restx import Namespace, Resource, fields
import os
from app import limiter

api = Namespace('model', description='Gestion des modèles')

model_info_model = api.model('ModelInfo', {
    'name': fields.String(description='Nom du modèle'),
    'type': fields.String(description='Type du modèle'),
    'size': fields.Integer(description='Taille du modèle en octets'),
    'available': fields.Boolean(description='Disponibilité du modèle')
})

models_list_model = api.model('ModelsList', {
    'models': fields.List(fields.Nested(model_info_model), description='Liste des modèles disponibles')
})

@api.route('/info')
class ModelInfo(Resource):
    @api.doc('get_models_info')
    @api.marshal_with(models_list_model, code=200)
    @limiter.limit("10 per minute")
    def get(self):
        """Récupère des informations sur les modèles disponibles"""
        try:
            models_info = []
            
            # Vérifier le modèle Gradient Boosting
            gb_model_path = os.path.join(current_app.config['GB_MODEL_DIR'], 'gradient_boosting_model.pkl')
            if os.path.exists(gb_model_path):
                models_info.append({
                    'name': 'Gradient Boosting',
                    'type': 'sklearn',
                    'size': os.path.getsize(gb_model_path),
                    'available': True
                })
            
            # Vérifier le modèle TensorFlow
            tf_model_path = os.path.join(current_app.config['TF_MODEL_DIR'], 'best_model.h5')
            if os.path.exists(tf_model_path):
                models_info.append({
                    'name': 'TensorFlow',
                    'type': 'keras',
                    'size': os.path.getsize(tf_model_path),
                    'available': True
                })
            
            # Vérifier le modèle TensorFlow Lite
            tflite_model_path = os.path.join(current_app.config['TF_MODEL_DIR'], 'model.tflite')
            if os.path.exists(tflite_model_path):
                models_info.append({
                    'name': 'TensorFlow Lite',
                    'type': 'tflite',
                    'size': os.path.getsize(tflite_model_path),
                    'available': True
                })
            
            return {'models': models_info}
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des informations sur les modèles: {str(e)}")

@api.route('/download/tflite')
class DownloadTFLiteModel(Resource):
    @api.doc('download_tflite_model')
    @limiter.limit("5 per day")
    def get(self):
        """Télécharge le modèle TensorFlow Lite pour une utilisation hors ligne"""
        try:
            tflite_model_path = os.path.join(current_app.config['TF_MODEL_DIR'], 'model.tflite')
            if not os.path.exists(tflite_model_path):
                api.abort(404, "Modèle TensorFlow Lite non trouvé")
            
            return send_file(
                tflite_model_path,
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name='crop_prediction_model.tflite'
            )
        except Exception as e:
            api.abort(500, f"Erreur lors du téléchargement du modèle: {str(e)}")