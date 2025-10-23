# Arquivo: app/routes/equipamento.py

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.models import Equipamento, Reserva, db, User
from datetime import datetime, timedelta
from sqlalchemy import func

equipamento_bp = Blueprint('equipamento', __name__, template_folder='../templates')


# --- Funções Auxiliares (Para evitar repetição de código) ---

def requires_admin(f):
    """Decorador para restringir o acesso apenas a administradores."""

    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado: Somente administradores podem realizar esta ação.', 'danger')
            return redirect(url_for('equipamento.dashboard'))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


# -----------------------------------------------
# DASHBOARD E LISTAGEM
# -----------------------------------------------

@equipamento_bp.route('/dashboard')
@login_required
def dashboard():
    total_equipamentos = Equipamento.query.count()
    equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
    reservas_ativas = Reserva.query.filter_by(finalizada=False).all()

    ultimas_reservas = Reserva.query.filter_by(finalizada=False).order_by(Reserva.data_inicio).limit(5).all()

    return render_template('index.html',
                           total_equipamentos=total_equipamentos,
                           equipamentos_disponiveis=equipamentos_disponiveis,
                           reservas_ativas=reservas_ativas,
                           ultimas_reservas=ultimas_reservas)


@equipamento_bp.route('/equipamentos')
@login_required
def listar_equipamentos():
    equipamentos = Equipamento.query.all()
    return render_template('equipamentos.html', equipamentos=equipamentos)


# -----------------------------------------------
# ROTAS DE EQUIPAMENTO (CRUD)
# -----------------------------------------------

@equipamento_bp.route('/equipamentos/novo', methods=['GET', 'POST'])
@requires_admin
def novo_equipamento():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        status = request.form.get('status', 'disponivel')

        novo = Equipamento(nome=nome, descricao=descricao, status=status)
        db.session.add(novo)
        db.session.commit()

        flash(f'Equipamento "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('equipamento.listar_equipamentos'))

    return render_template('novo_equipamento.html')


@equipamento_bp.route('/equipamentos/excluir/<int:equipamento_id>', methods=['POST'])
@requires_admin
def excluir_equipamento(equipamento_id):
    equipamento = Equipamento.query.get_or_404(equipamento_id)

    if equipamento.reservas:
        flash(f'Não é possível excluir "{equipamento.nome}" pois possui reservas associadas.', 'danger')
        return redirect(url_for('equipamento.listar_equipamentos'))

    db.session.delete(equipamento)
    db.session.commit()
    flash(f'Equipamento "{equipamento.nome}" excluído com sucesso.', 'success')
    return redirect(url_for('equipamento.listar_equipamentos'))


# -----------------------------------------------
# ROTAS DE RESERVA (CRUD)
# -----------------------------------------------

@equipamento_bp.route('/reservas')
@login_required
def reservas():
    reservas = Reserva.query.all()
    # Para o template reservas.html, o nome da função que calcula a duração é necessário
    return render_template('reservas.html', reservas=reservas, duracao_dias=Reserva.duracao_dias)


@equipamento_bp.route('/reservas/nova', methods=['GET', 'POST'])
@login_required
def nova_reserva():
    if request.method == 'POST':
        equipamento_id = request.form.get('equipamento_id')
        cliente_nome = request.form.get('cliente_nome')
        cliente_contato = request.form.get('cliente_contato')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')

        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido.', 'danger')
            return redirect(url_for('equipamento.nova_reserva'))

        if data_inicio > data_fim:
            flash('A data de início não pode ser posterior à data de término.', 'danger')
            return redirect(url_for('equipamento.nova_reserva'))

        equipamento = Equipamento.query.get_or_404(equipamento_id)

        if not equipamento.esta_disponivel(data_inicio, data_fim):
            flash(f'O equipamento "{equipamento.nome}" não está disponível no período solicitado.', 'danger')
            return redirect(url_for('equipamento.nova_reserva'))

        nova_reserva = Reserva(
            equipamento_id=equipamento.id,
            cliente_nome=cliente_nome,
            cliente_contato=cliente_contato,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        db.session.add(nova_reserva)
        db.session.commit()

        flash(f'Reserva de "{equipamento.nome}" para {cliente_nome} criada com sucesso!', 'success')
        return redirect(url_for('equipamento.reservas'))

    equipamentos = Equipamento.query.filter(Equipamento.status != 'manutencao').order_by(Equipamento.nome).all()
    return render_template('nova_reserva.html', equipamentos=equipamentos)


@equipamento_bp.route('/reservas/finalizar/<int:reserva_id>', methods=['POST'])
@login_required
def finalizar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    if reserva.finalizada:
        flash('Esta reserva já está finalizada.', 'warning')
        return redirect(url_for('equipamento.reservas'))

    reserva.finalizada = True
    db.session.commit()

    flash(f'Reserva de "{reserva.equipamento.nome}" finalizada com sucesso.', 'success')
    return redirect(url_for('equipamento.reservas'))


@equipamento_bp.route('/reservas/excluir/<int:reserva_id>', methods=['POST'])
@requires_admin
def excluir_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    equipamento_nome = reserva.equipamento.nome
    cliente_nome = reserva.cliente_nome

    db.session.delete(reserva)
    db.session.commit()

    flash(f'Reserva de "{equipamento_nome}" para {cliente_nome} excluída permanentemente.', 'success')
    return redirect(url_for('equipamento.reservas'))