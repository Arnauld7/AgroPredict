# recreate_model.py

import os
import pickle
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

def load_sklearn_model(model_dir="model"):
    """
    Charge le modèle sklearn GradientBoostingClassifier avec ses métadonnées
    """
    # Charger le modèle
    model_path = os.path.join(model_dir, 'gradient_boosting_model.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Charger le scaler
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    # Charger les métadonnées
    metadata_path = os.path.join(model_dir, 'metadata.pkl')
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    print(f"Modèle sklearn chargé avec succès du dossier '{model_dir}'")
    return model, scaler, metadata

def load_tensorflow_model(model_dir="tf_model"):
    """
    Charge le modèle TensorFlow avec ses métadonnées
    """
    # Charger le modèle
    model_path = os.path.join(model_dir, 'best_model.h5')
    model = tf.keras.models.load_model(model_path)
    
    # Charger les métadonnées
    metadata_path = os.path.join(model_dir, 'metadata.pkl')
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    print(f"Modèle TensorFlow chargé avec succès du dossier '{model_dir}'")
    return model, metadata

def predict_with_sklearn(model, scaler, metadata, N, P, K, temperature, humidity, ph, rainfall):
    """
    Prédit la culture avec le modèle sklearn
    """
    # Créer un tableau avec les valeurs d'entrée
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Standardiser les données d'entrée
    input_data_scaled = scaler.transform(input_data)
    
    # Faire la prédiction
    prediction = model.predict(input_data_scaled)
    probabilities = model.predict_proba(input_data_scaled)
    
    # Trouver l'indice de la classe prédite
    predicted_idx = np.argmax(probabilities[0])
    confidence = probabilities[0][predicted_idx]
    
    return prediction[0], confidence

def predict_with_tensorflow(model, metadata, N, P, K, temperature, humidity, ph, rainfall):
    """
    Prédit la culture avec le modèle TensorFlow
    """
    # Créer un tableau avec les valeurs d'entrée
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Standardiser les données d'entrée
    input_data_scaled = metadata['scaler'].transform(input_data)
    
    # Faire la prédiction
    prediction_proba = model.predict(input_data_scaled)
    prediction_idx = np.argmax(prediction_proba[0])
    
    # Convertir l'indice en nom de classe
    predicted_crop = metadata['class_names'][prediction_idx]
    confidence = prediction_proba[0][prediction_idx]
    
    return predicted_crop, confidence

def predict_with_tflite(tflite_model_path, metadata, N, P, K, temperature, humidity, ph, rainfall):
    """
    Prédit la culture avec le modèle TensorFlow Lite
    """
    # Charger le modèle TFLite
    interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
    interpreter.allocate_tensors()
    
    # Obtenir les détails des entrées et sorties
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Créer un tableau avec les valeurs d'entrée
    input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Standardiser les données d'entrée
    input_data_scaled = metadata['scaler'].transform(input_data).astype(np.float32)
    
    # Définir les données d'entrée
    interpreter.set_tensor(input_details[0]['index'], input_data_scaled)
    
    # Exécuter l'inférence
    interpreter.invoke()
    
    # Obtenir les résultats
    prediction_proba = interpreter.get_tensor(output_details[0]['index'])
    prediction_idx = np.argmax(prediction_proba[0])
    
    # Convertir l'indice en nom de classe
    predicted_crop = metadata['class_names'][prediction_idx]
    confidence = prediction_proba[0][prediction_idx]
    
    return predicted_crop, confidence

if __name__ == "__main__":
    # Exemple d'utilisation des modèles
    print("Démonstration de chargement et d'utilisation des modèles")
    
    # Paramètres de test
    N = 90
    P = 42
    K = 43
    temperature = 21
    humidity = 82
    ph = 6.5
    rainfall = 200
    
    print(f"\nPour les valeurs d'entrée N={N}, P={P}, K={K}, température={temperature}, humidité={humidity}, pH={ph}, précipitations={rainfall}")
    
    # Modèle sklearn
    try:
        sk_model, sk_scaler, sk_metadata = load_sklearn_model()
        sk_prediction, sk_confidence = predict_with_sklearn(sk_model, sk_scaler, sk_metadata, N, P, K, temperature, humidity, ph, rainfall)
        print(f"Prédiction sklearn: {sk_prediction} avec une confiance de {sk_confidence:.4f}")
    except Exception as e:
        print(f"Erreur lors du chargement/utilisation du modèle sklearn: {e}")
    
    # Modèle TensorFlow
    try:
        tf_model, tf_metadata = load_tensorflow_model()
        tf_prediction, tf_confidence = predict_with_tensorflow(tf_model, tf_metadata, N, P, K, temperature, humidity, ph, rainfall)
        print(f"Prédiction TensorFlow: {tf_prediction} avec une confiance de {tf_confidence:.4f}")
    except Exception as e:
        print(f"Erreur lors du chargement/utilisation du modèle TensorFlow: {e}")
    
    # Modèle TensorFlow Lite
    try:
        tflite_path = os.path.join("tf_model", "model.tflite")
        tflite_prediction, tflite_confidence = predict_with_tflite(tflite_path, tf_metadata, N, P, K, temperature, humidity, ph, rainfall)
        print(f"Prédiction TensorFlow Lite: {tflite_prediction} avec une confiance de {tflite_confidence:.4f}")
    except Exception as e:
        print(f"Erreur lors du chargement/utilisation du modèle TensorFlow Lite: {e}")
