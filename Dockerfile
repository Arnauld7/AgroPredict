# Utiliser une image Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Définir les variables d'environnement
ENV FLASK_ENV=prod
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV FLASK_DEBUG=False
ENV PYTHONUNBUFFERED=1

# Exposer le port
EXPOSE 5000

# Commande pour démarrer l'application
CMD ["python", "run.py"]