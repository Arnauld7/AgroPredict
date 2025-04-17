def validate_crop_params(data):
    """
    Valide les paramètres d'entrée pour la prédiction de cultures
    
    Args:
        data (dict): Dictionnaire contenant les paramètres à valider
        
    Returns:
        dict or None: Dictionnaire contenant les erreurs, ou None si tout est valide
    """
    errors = {}
    
    # Vérifier la présence de tous les paramètres requis
    required_params = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    for param in required_params:
        if param not in data:
            errors[param] = f"Le paramètre '{param}' est requis"
    
    # Si des paramètres sont manquants, retourner les erreurs
    if errors:
        return errors
    
    # Validation des plages de valeurs (basée sur les plages typiques)
    validations = {
        'N': (0, 300, "Le niveau d'azote doit être compris entre 0 et 300"),
        'P': (0, 300, "Le niveau de phosphore doit être compris entre 0 et 300"),
        'K': (0, 300, "Le niveau de potassium doit être compris entre 0 et 300"),
        'temperature': (-10, 60, "La température doit être comprise entre -10 et 60°C"),
        'humidity': (0, 100, "L'humidité doit être comprise entre 0 et 100%"),
        'ph': (0, 14, "Le pH doit être compris entre 0 et 14"),
        'rainfall': (0, 500, "Les précipitations doivent être comprises entre 0 et 500 mm")
    }
    
    # Vérifier que toutes les valeurs sont des nombres
    for param in required_params:
        try:
            # Convertir en float pour la validation
            value = float(data[param])
            
            # Vérifier si la valeur est dans la plage autorisée
            min_val, max_val, error_msg = validations[param]
            if value < min_val or value > max_val:
                errors[param] = error_msg
        except (ValueError, TypeError):
            errors[param] = f"La valeur de '{param}' doit être un nombre"
    
    # Si model_type est présent, vérifier qu'il est valide
    model_type = data.get('model_type')
    if model_type and model_type not in ['gradient_boosting', 'tensorflow', 'tensorflow_lite']:
        errors['model_type'] = "Le type de modèle doit être 'gradient_boosting', 'tensorflow' ou 'tensorflow_lite'"
    
    return errors if errors else None