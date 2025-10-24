from flask import Blueprint
from flask_restx import Namespace, Resource, fields
from app.models import Equipamento  # Importe seu modelo de Equipamento
from flask_restx import Api
import os


def load_readme():
    """Tenta carregar o conteúdo do README.md na raiz do projeto."""
    try:
        # Define o caminho absoluto para o README.md
        basedir = os.path.abspath(os.path.dirname(__file__))
        readme_path = os.path.join(basedir, '..\\..', 'guide.md')

        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return 'Falha ao carregar o README.md. Verifique se o arquivo existe na raiz do projeto.'


api_description_content = load_readme()

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializa o Flask-RESTX com o Blueprint
api = Api(
    api_bp,
    version='1.0',
    title='API de Gerenciamento de Brinquedos/Reservas',
    description=api_description_content,
    doc='/docs',  # A documentação interativa estará em /api/docs
    license='MIT'
)

# 1. Definição do Namespace
# O namespace ajuda a organizar os endpoints.
equipamento_ns = Namespace('equipamentos', description='Operações relacionadas a equipamentos (brinquedos)')

# 2. Definição do Modelo de Saída (Marshalling)
# Isso define a estrutura exata do JSON que a API retornará.
equipamento_model = api.model('Equipamento', {
    'id': fields.Integer(readonly=True, description='O identificador único do equipamento'),
    'nome': fields.String(required=True, description='Nome do equipamento'),
    'categoria': fields.String(description='Categoria do brinquedo'),
    'valor_diaria': fields.Float(description='Valor da diária de locação'),
    'status': fields.String(description='Status atual (Disponível, Em Uso, Manutenção)'),
})

api.add_namespace(equipamento_ns)
# 3. Definição do Resource (A Rota)
# Esta classe herda de Resource e define os métodos HTTP (GET, POST, etc.)
@api.route('/equipamentos')
class EquipamentoList(Resource):
    @api.doc('list_equipamentos')
    @api.marshal_list_with(equipamento_model)
    def get(self):
        """
        Lista todos os equipamentos disponíveis.
        """
        # Consulta ao banco de dados usando o modelo
        equipamentos = Equipamento.query.all()

        # O marshal_list_with converte a lista de objetos SQLAlchemy em JSON
        return equipamentos


# Opcional: Endpoint para um único equipamento (Busca por ID)
@api.route('/equipamento/<int:id>')
@api.param('id', 'O identificador do equipamento')
class EquipamentoDetail(Resource):
    @api.doc('get_equipamento')
    @api.marshal_with(equipamento_model)
    def get(self, id):
        """
        Obtém os detalhes de um equipamento específico.
        """
        equipamento = Equipamento.query.get_or_404(id)
        return equipamento