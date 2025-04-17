import pandas as pd
import numpy as np
import os
from flask import current_app

# Cache pour éviter de recharger le dataset à chaque appel
_crop_requirements_cache = None
_all_crops_cache = None

def get_crop_requirements():
    """
    Retourne les besoins moyens pour chaque culture à partir du dataset
    """
    global _crop_requirements_cache
    
    if _crop_requirements_cache is not None:
        return _crop_requirements_cache
    
    try:
        # Charger le dataset
        dataset_path = current_app.config['DATASET_PATH']
        
        if not os.path.exists(dataset_path):
            current_app.logger.error(f"Dataset non trouvé: {dataset_path}")
            return []
        
        df = pd.read_csv(dataset_path)
        
        # Grouper par culture et calculer les moyennes
        crop_means = df.groupby('label').mean().reset_index()
        
        # Convertir en liste de dictionnaires pour l'API
        crop_requirements = []
        for _, row in crop_means.iterrows():
            crop_requirements.append({
                'crop': row['label'],
                'N': float(row['N']),
                'P': float(row['P']),
                'K': float(row['K']),
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'ph': float(row['ph']),
                'rainfall': float(row['rainfall'])
            })
        
        # Mettre en cache
        _crop_requirements_cache = crop_requirements
        
        return crop_requirements
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des besoins des cultures: {e}")
        return []

def get_all_crops():
    """
    Retourne la liste de toutes les cultures disponibles
    """
    global _all_crops_cache
    
    if _all_crops_cache is not None:
        return _all_crops_cache
    
    try:
        # Obtenir les besoins des cultures
        crop_requirements = get_crop_requirements()
        
        # Extraire les noms des cultures
        crops = [req['crop'] for req in crop_requirements]
        
        # Mettre en cache
        _all_crops_cache = crops
        
        return crops
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération de la liste des cultures: {e}")
        return []