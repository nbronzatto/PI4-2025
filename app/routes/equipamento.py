# Arquivo: app/routes/equipamento.py

from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, make_response
from flask_login import login_required, current_user
from app.models import Equipamento, Reserva, db, User
from datetime import datetime, timedelta
from xhtml2pdf import pisa
import io # Para manipular o arquivo PDF em memória
from ..models import Reserva, Equipamento
from app.utils.email_tasks import send_confirmation_email

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

        try:
            send_confirmation_email(nova_reserva)
            flash(f'E-mail de confirmação enviado para o cliente: {nova_reserva.cliente_contato}', 'info')
        except Exception as e:
            # Loga o erro, mas não impede o fluxo do usuário
            flash(f'Falha ao enviar e-mail de confirmação (erro: {e}). Verifique as configurações de e-mail.',
                  'warning')
            print(f"Falha ao enviar e-mail de confirmação: {e}")


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


def render_to_pdf(template_src, context_dict={}):
    """Converte um template Jinja2 renderizado para um objeto PDF."""
    # 1. Renderiza o template HTML como string
    html = render_template(template_src, **context_dict)

    # 2. Cria um buffer de memória para armazenar o PDF
    result_file = io.BytesIO()

    # 3. Converte HTML para PDF
    pisa_status = pisa.CreatePDF(
        html,  # o conteúdo HTML renderizado
        dest=result_file  # o objeto de destino para armazenar o PDF
    )

    # 4. Retorna True/False e o buffer
    if pisa_status.err:
        return None  # Retorna None em caso de erro na conversão
    return result_file


@equipamento_bp.route('/relatorio_pdf', methods=['POST'])
# @login_required
def gerar_relatorio_pdf():
    # 1. Capturar os dados do formulário POST
    data_inicio_str = request.form.get('data_inicio')
    data_fim_str = request.form.get('data_fim')

    # 2. Iniciar a query e o filtro base
    query = Reserva.query

    # 3. Aplicar filtros de data (se fornecidos)
    data_inicio_obj = None
    if data_inicio_str:
        # Tenta converter a string para objeto date
        try:
            data_inicio_obj = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Reserva.data_fim >= data_inicio_obj)
        except ValueError:
            pass  # Ignora se a data for inválida

    data_fim_obj = None
    if data_fim_str:
        # Tenta converter a string para objeto date
        try:
            data_fim_obj = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            query = query.filter(Reserva.data_inicio <= data_fim_obj)
        except ValueError:
            pass  # Ignora se a data for inválida

    # 4. Executar a consulta
    reservas_filtradas = query.order_by(Reserva.data_inicio).all()

    # 5. Configurar o contexto para o template de PDF
    context = {
        'reservas_filtradas': reservas_filtradas,
        'data_inicio': data_inicio_obj.strftime('%d/%m/%Y') if data_inicio_obj else 'Todas',
        'data_fim': data_fim_obj.strftime('%d/%m/%Y') if data_fim_obj else 'Todas',
        'now': datetime.now  # Passa a função now para uso no template (se necessário)
    }

    # 6. Gera o PDF usando a função auxiliar
    pdf_buffer = render_to_pdf('relatorio_reservas.html', context)

    # 7. Retornar a resposta
    if not pdf_buffer:
        return "Erro ao gerar PDF", 500

    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers[
        'Content-Disposition'] = f'attachment; filename=relatorio_reservas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

    return response


# ... (Funções render_to_pdf e gerar_relatorio_pdf (reservas) já existentes) ...

@equipamento_bp.route('/relatorio_equipamento_pdf', methods=['POST'])
# @login_required
def gerar_relatorio_equipamento_pdf():
    # 1. Capturar os dados do formulário POST
    status_filtro = request.form.get('status_filtro')

    # 2. Iniciar a query
    query = Equipamento.query

    # 3. Aplicar filtro de status (se fornecido)
    if status_filtro:
        query = query.filter(Equipamento.status == status_filtro)

    # 4. Executar a consulta
    equipamentos_filtrados = query.order_by(Equipamento.nome).all()

    # 5. Configurar o contexto para o template de PDF
    context = {
        'equipamentos_filtrados': equipamentos_filtrados,
        'status_filtro': status_filtro,
        'now': datetime.now
    }

    # 6. Gera o PDF usando a função auxiliar
    pdf_buffer = render_to_pdf('relatorio_equipamentos.html', context)

    # 7. Retornar a resposta (Mesma lógica de download)
    if not pdf_buffer:
        return "Erro ao gerar PDF de equipamentos", 500

    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers[
        'Content-Disposition'] = f'attachment; filename=relatorio_brinquedos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

    return response