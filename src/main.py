from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões com o app
    db.init_app(app)
    bcrypt.init_app(app)  # <-- NOVO
    login_manager.init_app(app)  # <-- NOVO

    # Define para onde o Flask-Login deve redirecionar o usuário
    login_manager.login_view = 'auth.login'  # <-- Define a rota de login (será criada)
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    # -----------------------------------------------
    # Carregador de Usuário para Flask-Login
    # -----------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        # Esta função é chamada para recarregar o objeto User a partir do ID do usuário na sessão
        # O User deve ser importado aqui ou definido globalmente, dependendo da sua estrutura
        from models.user import User  # Supondo que a classe User esteja em models.py
        return User.query.get(int(user_id))

    # Importa e Registra Blueprints
    from routes.equipamento import equipamento_bp
    from routes.user import user_bp
    from routes.auth import auth_bp  # <-- NOVO BLUEPRINT

    app.register_blueprint(equipamento_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # <-- NOVO REGISTRO

    # Rota raiz (index)
    @app.route('/')
    def index():
        # Redireciona para a tela de gestão ou para a página de login
        if current_user.is_authenticated:
            return redirect(url_for('equipamento.dashboard'))
        return redirect(url_for('auth.login'))  # <-- Redireciona para login

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
