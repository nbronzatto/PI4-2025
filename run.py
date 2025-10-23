# Arquivo: run.py

from app import create_app, db

# Inicializa o app e cria as tabelas se necessário
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Cria o banco de dados e as tabelas (apenas se não existirem)
        db.create_all()
        # Lógica de criação do primeiro admin pode ir aqui se preferir.

    app.run(debug=True, use_reloader=False)