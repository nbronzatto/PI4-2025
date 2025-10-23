# Arquivo: app/routes/main.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db  # Importação corrigida
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('equipamento.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Bem-vindo(a), {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('equipamento.dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')

    return render_template('login.html', User=User)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))


# Rota de Registro (Permite apenas o primeiro registro para inicialização)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Bloqueia o registro se já houver usuários e não for um admin
    if User.query.first() and not request.args.get('allow_init') == '1':
        flash("O registro público está desativado.", 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já existe.', 'danger')
                return redirect(url_for('auth.register', allow_init=1))

            new_user = User(username=username, email=email)
            new_user.set_password(password)

            # Garante que o primeiro usuário seja o administrador
            if not User.query.first():
                new_user.is_admin = True

            db.session.add(new_user)
            db.session.commit()

            flash('Usuário registrado com sucesso! Faça o login.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao registrar. Tente outro email/usuário.', 'danger')

    return render_template('register.html')