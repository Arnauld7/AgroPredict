from functools import wraps
from flask import request, abort, current_app
import time
import hashlib
import re

# Dictionnaire simple pour stocker les tentatives de connexion (dans un vrai système, utilisez Redis ou une base de données)
request_counts = {}
blocked_ips = {}

def validate_input(input_str):
    """
    Valide l'entrée pour prévenir les injections
    
    Args:
        input_str (str): Chaîne à valider
        
    Returns:
        bool: True si la chaîne est sûre, False sinon
    """
    # Pattern de validation de base pour éviter les injections
    pattern = r'^[a-zA-Z0-9_\-.,\s]+$'
    
    if isinstance(input_str, str) and re.match(pattern, input_str):
        return True
    return False

def sanitize_input(input_str):
    """
    Nettoie l'entrée pour prévenir les injections
    
    Args:
        input_str (str): Chaîne à nettoyer
        
    Returns:
        str: Chaîne nettoyée
    """
    if not isinstance(input_str, str):
        return str(input_str)
    
    # Supprimer les caractères potentiellement dangereux
    sanitized = re.sub(r'[^\w\-.,\s]', '', input_str)
    return sanitized

def require_api_key(f):
    """
    Décorateur pour exiger une clé API
    Utiliser ce décorateur sur les routes qui nécessitent une authentification
    
    Note: Dans un environnement de production, utilisez un système d'authentification plus robuste
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        
        # Vérifier si la clé API est fournie et valide
        if not api_key or api_key != current_app.config.get('API_KEY'):
            abort(401, description="Clé API non valide ou manquante")
            
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=10, window=60):
    """
    Décorateur pour limiter le débit des requêtes
    
    Args:
        max_requests (int): Nombre maximal de requêtes dans la fenêtre de temps
        window (int): Fenêtre de temps en secondes
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtenir l'adresse IP du client
            ip = request.remote_addr
            
            # Vérifier si l'IP est bloquée
            if ip in blocked_ips and blocked_ips[ip] > time.time():
                abort(429, description="Trop de requêtes. Réessayez plus tard.")
            
            # Initialiser le compteur pour cette IP si nécessaire
            if ip not in request_counts:
                request_counts[ip] = []
            
            # Supprimer les requêtes anciennes
            now = time.time()
            request_counts[ip] = [t for t in request_counts[ip] if now - t < window]
            
            # Vérifier la limite de débit
            if len(request_counts[ip]) >= max_requests:
                # Bloquer l'IP pendant 10 minutes
                blocked_ips[ip] = now + 600  # 10 minutes
                abort(429, description="Trop de requêtes. Réessayez plus tard.")
            
            # Ajouter cette requête
            request_counts[ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator