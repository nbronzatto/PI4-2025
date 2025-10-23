# Arquivo: app/routes/user_api.py

from flask import Blueprint, jsonify, request, abort
from app.models import User, db
from flask_login import login_required, current_user  # Autenticação provisória via sessão

user_api_bp = Blueprint('user_api', __name__)


@user_api_bp.before_request
@login_required
def before_request():
    """Protege toda a API contra usuários não logados."""
    if not current_user.is_admin:
        return jsonify({'message': 'Acesso de API negado. Requer administrador logado.'}), 403


# Criar Usuário (Permitido apenas a admins)
@user_api_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Dados incompletos'}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Usuário ou Email já existe'}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


# Listar Usuários
@user_api_bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# Obter Usuário por ID
@user_api_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


# Atualizar Usuário (PATCH)
@user_api_bp.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'password' in data:
        user.set_password(data['password'])

    if 'is_admin' in data and current_user.id != user_id:  # Não permite auto-rebaixamento
        user.is_admin = data['is_admin']

    # Outros campos...

    db.session.commit()
    return jsonify(user.to_dict()), 200


# Excluir Usuário
@user_api_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        return jsonify({'message': 'Não é possível excluir seu próprio usuário logado.'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuário excluído'}), 204