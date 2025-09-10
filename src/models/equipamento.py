from src.database import db
from datetime import datetime

class Equipamento(db.Model):
    __tablename__ = 'equipamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='disponivel')  # disponivel, reservado, manutencao
    
    # Relacionamento com reservas
    reservas = db.relationship('Reserva', backref='equipamento', lazy=True)
    
    def __repr__(self):
        return f'<Equipamento {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'status': self.status
        }
    
    def esta_disponivel(self):
        return self.status == 'disponivel'


class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamentos.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_contato = db.Column(db.String(100), nullable=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reserva {self.cliente_nome} - {self.equipamento.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipamento_id': self.equipamento_id,
            'equipamento_nome': self.equipamento.nome if self.equipamento else None,
            'data_inicio': self.data_inicio.strftime('%Y-%m-%d') if self.data_inicio else None,
            'data_fim': self.data_fim.strftime('%Y-%m-%d') if self.data_fim else None,
            'cliente_nome': self.cliente_nome,
            'cliente_contato': self.cliente_contato,
            'data_criacao': self.data_criacao.strftime('%Y-%m-%d %H:%M:%S') if self.data_criacao else None
        }
    
    def duracao_dias(self):
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days + 1
        return 0

