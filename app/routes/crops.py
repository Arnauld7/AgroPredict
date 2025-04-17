from flask_restx import Namespace, Resource, fields
from app.services.crop_data import get_crop_requirements, get_all_crops
from app import limiter

api = Namespace('crops', description='Informations sur les cultures agricoles')

# Modèle pour les exigences des cultures
crop_req_model = api.model('CropRequirements', {
    'N': fields.Float(description='Niveau moyen d\'azote requis'),
    'P': fields.Float(description='Niveau moyen de phosphore requis'),
    'K': fields.Float(description='Niveau moyen de potassium requis'),
    'temperature': fields.Float(description='Température moyenne requise (°C)'),
    'humidity': fields.Float(description='Humidité moyenne requise (%)'),
    'ph': fields.Float(description='pH moyen du sol requis'),
    'rainfall': fields.Float(description='Précipitations moyennes requises (mm)')
})

all_crops_model = api.model('AllCrops', {
    'crops': fields.List(fields.String, description='Liste de toutes les cultures disponibles')
})

@api.route('')
class CropRequirements(Resource):
    @api.doc('get_crop_requirements')
    @api.marshal_with(crop_req_model, as_list=True, code=200)
    @limiter.limit("20 per minute")
    def get(self):
        """Récupère les besoins moyens pour toutes les cultures"""
        try:
            crop_requirements = get_crop_requirements()
            return crop_requirements
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des besoins des cultures: {str(e)}")

@api.route('/list')
class CropList(Resource):
    @api.doc('get_all_crops')
    @api.marshal_with(all_crops_model, code=200)
    @limiter.limit("20 per minute")
    def get(self):
        """Récupère la liste de toutes les cultures disponibles"""
        try:
            crops = get_all_crops()
            return {'crops': crops}
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération de la liste des cultures: {str(e)}")

@api.route('/<string:crop_name>')
@api.param('crop_name', 'Nom de la culture')
class CropRequirement(Resource):
    @api.doc('get_crop_requirement')
    @api.marshal_with(crop_req_model, code=200)
    @limiter.limit("20 per minute")
    def get(self, crop_name):
        """Récupère les besoins moyens pour une culture spécifique"""
        try:
            crop_requirements = get_crop_requirements()
            for req in crop_requirements:
                if req.get('crop').lower() == crop_name.lower():
                    return req
            api.abort(404, f"Culture '{crop_name}' non trouvée")
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des besoins de la culture: {str(e)}")