from app import create_app
import os

app = create_app(os.getenv('FLASK_ENV', 'dev'))

if __name__ == '__main__':
    # Configuration du serveur de développement
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    app.run(host=host, port=port, debug=debug)