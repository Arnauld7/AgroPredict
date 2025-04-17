import unittest
import json
from app import create_app

class TestCropsAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_get_all_crops_requirements(self):
        """Test de la route /crops pour récupérer les besoins de toutes les cultures"""
        response = self.client.get('/crops')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        
        if len(data) > 0:
            # Vérifier la structure des données pour le premier élément
            first_crop = data[0]
            self.assertIn('crop', first_crop)
            self.assertIn('N', first_crop)
            self.assertIn('P', first_crop)
            self.assertIn('K', first_crop)
            self.assertIn('temperature', first_crop)
            self.assertIn('humidity', first_crop)
            self.assertIn('ph', first_crop)
            self.assertIn('rainfall', first_crop)
    
    def test_get_crops_list(self):
        """Test de la route /crops/list pour récupérer la liste des cultures"""
        response = self.client.get('/crops/list')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('crops', data)
        self.assertIsInstance(data['crops'], list)
    
    def test_get_specific_crop(self):
        """Test de la route /crops/{crop_name} pour récupérer les besoins d'une culture spécifique"""
        # D'abord, obtenez la liste des cultures disponibles
        response = self.client.get('/crops/list')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if 'crops' in data and len(data['crops']) > 0:
            # Prendre la première culture
            crop_name = data['crops'][0]
            
            # Récupérer les besoins de cette culture
            response = self.client.get(f'/crops/{crop_name}')
            self.assertEqual(response.status_code, 200)
            crop_data = json.loads(response.data)
            
            # Vérifier la structure des données
            self.assertIn('crop', crop_data)
            self.assertEqual(crop_data['crop'], crop_name)
            self.assertIn('N', crop_data)
            self.assertIn('P', crop_data)
            self.assertIn('K', crop_data)
            self.assertIn('temperature', crop_data)
            self.assertIn('humidity', crop_data)
            self.assertIn('ph', crop_data)
            self.assertIn('rainfall', crop_data)
        
        # Tester avec une culture inexistante
        response = self.client.get('/crops/inexistant_crop')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()