from flask_sqlalchemy import SQLAlchemy

# Instância única do SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Inicializar banco de dados com a aplicação Flask"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

