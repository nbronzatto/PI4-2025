
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from datetime import datetime, date


equipamento_bp = Blueprint('equipamento', __name__)

@equipamento_bp.route('/')
@login_required
def index():
    """Página principal com listagem de equipamentos e reservas"""
    equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
    reservas_ativas = Reserva.query.join(Equipamento).all()
    
    return render_template('index.html', 
                         equipamentos=equipamentos_disponiveis,
                         reservas=reservas_ativas)

@equipamento_bp.route('/equipamentos')
@login_required
def listar_equipamentos():
    """Lista todos os equipamentos"""
    equipamentos = Equipamento.query.all()
    return render_template('equipamentos.html', equipamentos=equipamentos)

@equipamento_bp.route('/equipamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():
    """Cadastrar novo equipamento"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        status = request.form.get('status', 'disponivel')
        
        if not nome:
            flash('Nome do equipamento é obrigatório!', 'error')
            return render_template('novo_equipamento.html')
        
        equipamento = Equipamento(
            nome=nome,
            descricao=descricao,
            status=status
        )
        
        try:
            db.session.add(equipamento)
            db.session.commit()
            flash(f'Equipamento "{nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('equipamento.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar equipamento. Tente novamente.', 'error')
            return render_template('novo_equipamento.html')
    
    return render_template('novo_equipamento.html')

@equipamento_bp.route('/reservas')
def listar_reservas():
    """Lista todas as reservas"""
    reservas = Reserva.query.join(Equipamento).all()
    return render_template('reservas.html', reservas=reservas)

@equipamento_bp.route('/reservas/nova', methods=['GET', 'POST'])
def nova_reserva():
    """Criar nova reserva"""
    if request.method == 'POST':
        equipamento_id = request.form.get('equipamento_id')
        data_inicio_str = request.form.get('data_inicio')
        data_fim_str = request.form.get('data_fim')
        cliente_nome = request.form.get('cliente_nome')
        cliente_contato = request.form.get('cliente_contato')
        
        # Validações
        if not all([equipamento_id, data_inicio_str, data_fim_str, cliente_nome]):
            flash('Todos os campos obrigatórios devem ser preenchidos!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        if data_inicio > data_fim:
            flash('Data de início não pode ser posterior à data de fim!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        if data_inicio < date.today():
            flash('Data de início não pode ser anterior à data atual!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        # Verificar se o equipamento existe e está disponível
        equipamento = Equipamento.query.get(equipamento_id)
        if not equipamento:
            flash('Equipamento não encontrado!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        if not equipamento.esta_disponivel():
            flash('Equipamento não está disponível para reserva!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        # Verificar conflitos de reserva
        conflito = Reserva.query.filter(
            Reserva.equipamento_id == equipamento_id,
            Reserva.data_inicio <= data_fim,
            Reserva.data_fim >= data_inicio
        ).first()
        
        if conflito:
            flash('Já existe uma reserva para este equipamento no período selecionado!', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
        
        # Criar reserva
        reserva = Reserva(
            equipamento_id=equipamento_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            cliente_nome=cliente_nome,
            cliente_contato=cliente_contato
        )
        
        try:
            db.session.add(reserva)
            # Atualizar status do equipamento para reservado
            equipamento.status = 'reservado'
            db.session.commit()
            flash(f'Reserva criada com sucesso para {cliente_nome}!', 'success')
            return redirect(url_for('equipamento.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar reserva. Tente novamente.', 'error')
            equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
            return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis)
    
    # GET request - mostrar formulário
    equipamentos_disponiveis = Equipamento.query.filter_by(status='disponivel').all()
    data_hoje = date.today().strftime('%Y-%m-%d')
    return render_template('nova_reserva.html', equipamentos=equipamentos_disponiveis, data_hoje=data_hoje)

@equipamento_bp.route('/equipamentos/<int:equipamento_id>/excluir', methods=['POST'])
def excluir_equipamento(equipamento_id):
    try:
        equipamento = Equipamento.query.get_or_404(equipamento_id)
        
        # Verificar se há reservas ativas para este equipamento
        reservas_ativas = Reserva.query.filter_by(equipamento_id=equipamento_id).all()
        
        if reservas_ativas:
            flash(f'Não é possível excluir o equipamento "{equipamento.nome}" pois há reservas ativas associadas a ele.', 'error')
            return redirect(url_for('equipamento.listar_equipamentos'))
        
        # Excluir o equipamento
        db.session.delete(equipamento)
        db.session.commit()
        
        flash(f'Equipamento "{equipamento.nome}" excluído com sucesso!', 'success')
        return redirect(url_for('equipamento.listar_equipamentos'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir equipamento. Tente novamente.', 'error')
        return redirect(url_for('equipamento.listar_equipamentos'))

@equipamento_bp.route('/reservas/<int:reserva_id>/excluir', methods=['POST'])
def excluir_reserva(reserva_id):
    try:
        reserva = Reserva.query.get_or_404(reserva_id)
        equipamento = reserva.equipamento
        
        # Liberar o equipamento (voltar status para disponível)
        equipamento.status = 'disponivel'
        
        # Excluir a reserva
        db.session.delete(reserva)
        db.session.commit()
        
        flash(f'Reserva excluída com sucesso! Equipamento "{equipamento.nome}" está novamente disponível.', 'success')
        return redirect(url_for('equipamento.reservas'))
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir reserva. Tente novamente.', 'error')
        return redirect(url_for('equipamento.reservas'))

@equipamento_bp.route('/reservas/<int:reserva_id>/finalizar', methods=['POST'])
def finalizar_reserva(reserva_id):
    """Finalizar uma reserva e liberar o equipamento"""
    reserva = Reserva.query.get_or_404(reserva_id)
    equipamento = reserva.equipamento
    
    try:
        # Remover a reserva
        db.session.delete(reserva)
        # Liberar o equipamento
        equipamento.status = 'disponivel'
        db.session.commit()
        flash('Reserva finalizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao finalizar reserva. Tente novamente.', 'error')
    
    return redirect(url_for('equipamento.dashboard'))

# API endpoints para dados JSON (opcional)
@equipamento_bp.route('/api/equipamentos')
def api_equipamentos():
    """API para listar equipamentos em JSON"""
    equipamentos = Equipamento.query.all()
    return jsonify([eq.to_dict() for eq in equipamentos])

@equipamento_bp.route('/api/reservas')
def api_reservas():
    """API para listar reservas em JSON"""
    reservas = Reserva.query.all()
    return jsonify([res.to_dict() for res in reservas])

