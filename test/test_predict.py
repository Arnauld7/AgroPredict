import unittest
import json
from app import create_app

class TestPredictAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_predict_post(self):
        """Test de la route /predict avec une requête POST"""
        payload = {
            'N': 90,
            'P': 42,
            'K': 43,
            'temperature': 21,
            'humidity': 82,
            'ph': 6.5,
            'rainfall': 200,
            'model_type': 'gradient_boosting'
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('crop', data)
        self.assertIn('confidence', data)
        self.assertIn('model_used', data)
        self.assertIn('input_parameters', data)
        
    def test_predict_invalid_parameters(self):
        """Test de la route /predict avec des paramètres invalides"""
        # Paramètres manquants
        payload = {
            'N': 90,
            'P': 42,
            # K manquant
            'temperature': 21,
            'humidity': 82,
            'ph': 6.5,
            'rainfall': 200
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Valeurs hors limites
        payload = {
            'N': 90,
            'P': 42,
            'K': 43,
            'temperature': 100,  # Température trop élevée
            'humidity': 82,
            'ph': 6.5,
            'rainfall': 200
        }
        
        response = self.client.post(
            '/predict',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_predict_simple_get(self):
        """Test de la route /predict/simple avec une requête GET"""
        response = self.client.get(
            '/predict/simple?N=90&P=42&K=43&temperature=21&humidity=82&ph=6.5&rainfall=200&model_type=gradient_boosting'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('crop', data)
        self.assertIn('confidence', data)
        self.assertIn('model_used', data)
        self.assertIn('input_parameters', data)

if __name__ == '__main__':
    unittest.main()