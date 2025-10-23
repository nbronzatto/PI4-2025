# Arquivo: app/models.py

from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime, timedelta


# -----------------------------------------------
# MODELO DE USUÁRIO (Autenticação)
# -----------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }


# -----------------------------------------------
# MODELO DE EQUIPAMENTO
# -----------------------------------------------
class Equipamento(db.Model):
    __tablename__ = 'equipamento'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), default='disponivel')  # disponivel, manutencao
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    reservas = db.relationship('Reserva', backref='equipamento', lazy=True)

    def esta_disponivel(self, data_inicio, data_fim):
        """Verifica se há conflito de reservas para o período."""
        conflitos = Reserva.query.filter_by(equipamento_id=self.id).filter(
            db.or_(
                Reserva.data_inicio.between(data_inicio, data_fim - timedelta(seconds=1)),
                Reserva.data_fim.between(data_inicio + timedelta(seconds=1), data_fim)
            )
        ).first()
        return conflitos is None

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status,
            'descricao': self.descricao,
            'data_cadastro': self.data_cadastro.isoformat()
        }


# -----------------------------------------------
# MODELO DE RESERVA
# -----------------------------------------------
class Reserva(db.Model):
    __tablename__ = 'reserva'
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamento.id'), nullable=False)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_contato = db.Column(db.String(100))
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    finalizada = db.Column(db.Boolean, default=False)

    def duracao_dias(self):
        """Calcula a duração da reserva em dias."""
        # Adiciona 1 dia para incluir o dia de término
        return (self.data_fim - self.data_inicio).days + 1

    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'cliente_nome': self.cliente_nome,
            'data_inicio': self.data_inicio.isoformat(),
            'data_fim': self.data_fim.isoformat(),
            'finalizada': self.finalizada
        }