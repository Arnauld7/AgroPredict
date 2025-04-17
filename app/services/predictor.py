import os
import pickle
import numpy as np
import tensorflow as tf
from flask import current_app

class CropPredictor:
    """
    Une classe pour charger et utiliser différents modèles de prédiction de cultures
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Singleton pattern pour éviter de recharger les modèles à chaque appel"""
        if cls._instance is None:
            cls._instance = CropPredictor()
        return cls._instance
    
    def __init__(self):
        # Modèles disponibles
        self.models = {
            'gradient_boosting': None,
            'tensorflow': None,
            'tensorflow_lite': None
        }
        
        # Métadonnées associées
        self.metadata = {
            'gradient_boosting': None,
            'tensorflow': None
        }
        
        # Scalers pour la standardisation
        self.scalers = {
            'gradient_boosting': None,
            'tensorflow': None
        }
        
        # Tentative de chargement des modèles disponibles
        self._load_models()
    
    def _load_models(self):
        """Charge tous les modèles disponibles"""
        # Gradient Boosting (scikit-learn)
        try:
            gb_model_dir = current_app.config['GB_MODEL_DIR']
            gb_model_path = os.path.join(gb_model_dir, 'gradient_boosting_model.pkl')
            scaler_path = os.path.join(gb_model_dir, 'scaler.pkl')
            metadata_path = os.path.join(gb_model_dir, 'metadata.pkl')
            
            if os.path.exists(gb_model_path) and os.path.exists(scaler_path) and os.path.exists(metadata_path):
                # Charger le modèle
                with open(gb_model_path, 'rb') as f:
                    self.models['gradient_boosting'] = pickle.load(f)
                
                # Charger le scaler
                with open(scaler_path, 'rb') as f:
                    self.scalers['gradient_boosting'] = pickle.load(f)
                
                # Charger les métadonnées
                with open(metadata_path, 'rb') as f:
                    self.metadata['gradient_boosting'] = pickle.load(f)
                
                current_app.logger.info("Modèle Gradient Boosting chargé avec succès.")
            else:
                current_app.logger.warning("Modèle Gradient Boosting ou ses fichiers associés non trouvés.")
        except Exception as e:
            current_app.logger.error(f"Erreur lors du chargement du modèle Gradient Boosting: {e}")
        
        # TensorFlow
        try:
            tf_model_dir = current_app.config['TF_MODEL_DIR']
            tf_model_path = os.path.join(tf_model_dir, 'best_model.h5')
            tf_metadata_path = os.path.join(tf_model_dir, 'metadata.pkl')
            
            if os.path.exists(tf_model_path) and os.path.exists(tf_metadata_path):
                # Charger le modèle
                self.models['tensorflow'] = tf.keras.models.load_model(tf_model_path)
                
                # Charger les métadonnées (contient aussi le scaler)
                with open(tf_metadata_path, 'rb') as f:
                    self.metadata['tensorflow'] = pickle.load(f)
                
                # Récupérer le scaler des métadonnées
                self.scalers['tensorflow'] = self.metadata['tensorflow']['scaler']
                
                current_app.logger.info("Modèle TensorFlow chargé avec succès.")
            else:
                current_app.logger.warning("Modèle TensorFlow ou ses fichiers associés non trouvés.")
        except Exception as e:
            current_app.logger.error(f"Erreur lors du chargement du modèle TensorFlow: {e}")
        
        # TensorFlow Lite
        try:
            tflite_path = os.path.join(tf_model_dir, 'model.tflite')
            
            if os.path.exists(tflite_path):
                # Charger le modèle TFLite
                self.models['tensorflow_lite'] = tflite_path
                current_app.logger.info("Modèle TensorFlow Lite chargé avec succès.")
            else:
                current_app.logger.warning("Modèle TensorFlow Lite non trouvé.")
        except Exception as e:
            current_app.logger.error(f"Erreur lors du chargement du modèle TensorFlow Lite: {e}")
    
    def predict_crop_sklearn(self, N, P, K, temperature, humidity, ph, rainfall):
        """
        Prédit la culture en utilisant le modèle scikit-learn
        """
        if self.models['gradient_boosting'] is None or self.scalers['gradient_boosting'] is None:
            raise ValueError("Le modèle Gradient Boosting n'est pas chargé")
        
        # Créer un tableau avec les valeurs d'entrée
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        
        # Standardiser les données d'entrée
        input_data_scaled = self.scalers['gradient_boosting'].transform(input_data)
        
        # Faire la prédiction
        prediction = self.models['gradient_boosting'].predict(input_data_scaled)
        probabilities = self.models['gradient_boosting'].predict_proba(input_data_scaled)
        
        # Trouver l'indice de la classe prédite
        predicted_idx = np.argmax(probabilities[0])
        confidence = probabilities[0][predicted_idx]
        
        return prediction[0], confidence
    
    def predict_crop_tensorflow(self, N, P, K, temperature, humidity, ph, rainfall):
        """
        Prédit la culture en utilisant le modèle TensorFlow
        """
        if self.models['tensorflow'] is None or self.scalers['tensorflow'] is None:
            raise ValueError("Le modèle TensorFlow n'est pas chargé")
        
        # Créer un tableau avec les valeurs d'entrée
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        
        # Standardiser les données d'entrée
        input_data_scaled = self.scalers['tensorflow'].transform(input_data)
        
        # Faire la prédiction
        prediction_proba = self.models['tensorflow'].predict(input_data_scaled)
        prediction_idx = np.argmax(prediction_proba[0])
        
        # Convertir l'indice en nom de classe
        predicted_crop = self.metadata['tensorflow']['class_names'][prediction_idx]
        confidence = prediction_proba[0][prediction_idx]
        
        return predicted_crop, confidence
    
    def predict_crop_tflite(self, N, P, K, temperature, humidity, ph, rainfall):
        """
        Prédit la culture en utilisant le modèle TensorFlow Lite
        """
        if self.models['tensorflow_lite'] is None or self.scalers['tensorflow'] is None:
            raise ValueError("Le modèle TensorFlow Lite n'est pas chargé")
        
        # Charger l'interpréteur TFLite
        interpreter = tf.lite.Interpreter(model_path=self.models['tensorflow_lite'])
        interpreter.allocate_tensors()
        
        # Obtenir les détails des entrées et sorties
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Créer un tableau avec les valeurs d'entrée
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        
        # Standardiser les données d'entrée
        input_data_scaled = self.scalers['tensorflow'].transform(input_data).astype(np.float32)
        
        # Définir les données d'entrée
        interpreter.set_tensor(input_details[0]['index'], input_data_scaled)
        
        # Exécuter l'inférence
        interpreter.invoke()
        
        # Obtenir les résultats
        prediction_proba = interpreter.get_tensor(output_details[0]['index'])
        prediction_idx = np.argmax(prediction_proba[0])
        
        # Convertir l'indice en nom de classe
        predicted_crop = self.metadata['tensorflow']['class_names'][prediction_idx]
        confidence = prediction_proba[0][prediction_idx]
        
        return predicted_crop, confidence
    
    def predict_crop(self, N, P, K, temperature, humidity, ph, rainfall, model_type='gradient_boosting'):
        """
        Prédit la culture en utilisant le modèle spécifié
        """
        if model_type == 'gradient_boosting':
            return self.predict_crop_sklearn(N, P, K, temperature, humidity, ph, rainfall)
        elif model_type == 'tensorflow':
            return self.predict_crop_tensorflow(N, P, K, temperature, humidity, ph, rainfall)
        elif model_type == 'tensorflow_lite':
            return self.predict_crop_tflite(N, P, K, temperature, humidity, ph, rainfall)
        else:
            raise ValueError(f"Type de modèle inconnu: {model_type}")

def get_predictor():
    """
    Retourne l'instance unique de CropPredictor
    """
    return CropPredictor.get_instance()