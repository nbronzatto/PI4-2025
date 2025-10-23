from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from ..models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Login bem-sucedido
            login_user(user, remember=True)  # Mantenha o usuário logado
            flash('Login realizado com sucesso!', 'success')

            # Redireciona para a página que o usuário tentou acessar (next) ou para a home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('equipamento.dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))


# Rota de Registro (apenas para inicialização do sistema)
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Esta rota deve ser restrita ou removida em produção após o primeiro admin ser criado
    if User.query.first() and not request.args.get('allow_init'):
        flash("O registro está desativado. Contate o administrador.", 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # O primeiro usuário criado é definido como admin (exemplo simples de inicialização)
        if not User.query.first():
            new_user.is_admin = True

        db.session.add(new_user)
        db.session.commit()

        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')