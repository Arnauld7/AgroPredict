import unittest
import json
import os
from app import create_app

class TestModelAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_get_models_info(self):
        """Test de la route /model/info pour obtenir des informations sur les modèles"""
        response = self.client.get('/model/info')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('models', data)
        self.assertIsInstance(data['models'], list)
        
        if len(data['models']) > 0:
            # Vérifier la structure des données pour le premier modèle
            first_model = data['models'][0]
            self.assertIn('name', first_model)
            self.assertIn('type', first_model)
            self.assertIn('size', first_model)
            self.assertIn('available', first_model)
    
    def test_download_tflite_model(self):
        """Test de la route /model/download/tflite pour télécharger le modèle TFLite"""
        # Vérifier si le modèle TFLite existe
        tf_model_dir = self.app.config['TF_MODEL_DIR']
        tflite_path = os.path.join(tf_model_dir, 'model.tflite')
        
        if os.path.exists(tflite_path):
            response = self.client.get('/model/download/tflite')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('application/octet-stream', response.headers['Content-Type'])
            self.assertIn('attachment', response.headers['Content-Disposition'])
            self.assertIn('crop_prediction_model.tflite', response.headers['Content-Disposition'])
        else:
            # Si le modèle n'existe pas, la route devrait renvoyer 404
            response = self.client.get('/model/download/tflite')
            self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()