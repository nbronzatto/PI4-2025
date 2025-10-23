# Arquivo: app/__init__.py

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
import os

# Inicialização das Extensões fora da função para uso global
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app(config_class=None):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # Configurações

    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões com o app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Configurações do Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    # -----------------------------------------------
    # Carregador de Usuário (Importação dentro da função para evitar Circular Import)
    # -----------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # -----------------------------------------------
    # Registro de Blueprints
    # -----------------------------------------------
    from app.routes.main import auth_bp
    from app.routes.equipamento import equipamento_bp
    from app.routes.user_api import user_api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(equipamento_bp)
    app.register_blueprint(user_api_bp, url_prefix='/api/users')

    # Rota raiz (index) - Redireciona para o dashboard ou login
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # Assumindo que a rota index do equipamento é o dashboard
            return redirect(url_for('equipamento.dashboard'))
        return redirect(url_for('auth.login'))

    return app