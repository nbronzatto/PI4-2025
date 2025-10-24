from flask_mail import Message
from datetime import datetime, timedelta
from app.__init__ import mail, scheduler  # Importe o objeto mail e scheduler
from app.models import Reserva  # Importe seu modelo de Reserva


# --- 1. Função Genérica de Envio ---

def send_email(subject, recipients, html_body):
    """Envia um e-mail com o corpo em HTML."""
    try:
        msg = Message(subject, recipients=recipients)
        msg.html = html_body
        mail.send(msg)
        print(f"E-mail '{subject}' enviado com sucesso para {recipients[0]}")
    except Exception as e:
        print(f"ERRO ao enviar e-mail '{subject}': {e}")


# --- 2. Função de Envio de Confirmação Imediata ---

def send_confirmation_email(reserva):
    """Envia e-mail imediatamente após a criação da reserva."""
    subject = f"Confirmação de Reserva: {reserva.equipamento.nome}"
    recipients = [reserva.cliente_contato]

    # Formatação das datas
    data_inicio_fmt = reserva.data_inicio.strftime('%d/%m/%Y')
    data_fim_fmt = reserva.data_fim.strftime('%d/%m/%Y')

    html_body = f"""
    <h2>Sua Reserva está Confirmada!</h2>
    <p>Olá {reserva.cliente_nome},</p>
    <p>Confirmamos a sua reserva para o seguinte item:</p>
    <ul>
        <li><strong>Brinquedo:</strong> {reserva.equipamento.nome}</li>
        <li><strong>Período:</strong> De {data_inicio_fmt} a {data_fim_fmt} ({reserva.duracao_dias()} dias)</li>        
    </ul>
    <p>Detalhes para retirada serão enviados em um lembrete no dia anterior ao início da reserva.</p>
    <p>Obrigado!</p>
    """
    send_email(subject, recipients, html_body)


# --- 3. Função de Verificação de Lembretes (Tarefa Agendada) ---

def check_for_reminders(app):
    """Tarefa diária que verifica reservas que começam amanhã."""
    with app.app_context():
        # Define "amanhã"
        amanha = (datetime.now() + timedelta(days=1)).date()

        # Consulta reservas que iniciam amanhã
        reservas_amanha = Reserva.query.filter(
            Reserva.data_inicio == amanha
        ).all()

        print(f"Verificação de lembretes: {len(reservas_amanha)} reservas encontradas para amanhã ({amanha}).")

        for reserva in reservas_amanha:
            send_reminder_email(reserva)


def send_reminder_email(reserva):
    """Envia o e-mail de lembrete 1 dia antes da retirada."""
    subject = f"Lembrete: Sua Reserva de {reserva.equipamento.nome} Começa Amanhã!"
    recipients = [reserva.cliente_email]

    data_inicio_fmt = reserva.data_inicio.strftime('%d/%m/%Y')

    html_body = f"""
    <h2>Prezado(a) {reserva.cliente_nome},</h2>
    <p>Sua reserva está marcada para começar **amanhã**, {data_inicio_fmt}.</p>
    <p>Por favor, dirija-se ao nosso ponto de retirada com os seguintes detalhes:</p>

    <h3>Detalhes da Retirada:</h3>
    <ul>
        <li><strong>Item Reservado:</strong> {reserva.equipamento.nome}</li>
        <li><strong>Local de Retirada:</strong> [Seu Endereço de Retirada Aqui]</li>
        <li><strong>Horário:</strong> [Seu Horário de Funcionamento Aqui]</li>
        <li><strong>Documentação Necessária:</strong> Documento de Identidade e Comprovante de Residência.</li>
    </ul>
    <p>Em caso de dúvidas, responda a este e-mail ou ligue para [Seu Telefone].</p>
    """
    send_email(subject, recipients, html_body)


# --- 4. Agendamento da Tarefa ---

def agendar_tarefas_diarias(app):
    """Adiciona a tarefa diária ao APScheduler."""
    # Remove qualquer tarefa anterior com o mesmo ID
    if scheduler.get_job('daily_reminder_check'):
        scheduler.remove_job('daily_reminder_check')

    # Agenda para rodar todos os dias às 8:00 (ajuste o horário conforme necessário)
    scheduler.add_job(
        id='daily_reminder_check',
        func=check_for_reminders,
        args=[app],
        trigger='cron',
        hour=8,
        minute=0,
        misfire_grace_time=3600  # Executa mesmo se falhar por 1h
    )