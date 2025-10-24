# Sistema de Gestão de Locação de Brinquedos (PI4-2025)

Este é um sistema web e API RESTful desenvolvido em Python com o framework Flask para o gerenciamento completo de equipamentos (brinquedos) e reservas.

## ⚙️ Tecnologias Utilizadas

* **Backend:** Python
* **Framework Web:** Flask
* **Banco de Dados:** SQLite (configurável para PostgreSQL/MySQL via SQLAlchemy)
* **ORM:** Flask-SQLAlchemy
* **Documentação API:** Flask-RESTX (Swagger UI)
* **E-mails:** Flask-Mail
* **Tarefas Agendadas:** Flask-APScheduler
* **Relatórios:** Flask + WeasyPrint (para geração de PDF)
* **Frontend (Templates):** Jinja2 + Bootstrap 5

## 🚀 Configuração e Instalação

### Pré-requisitos

* Python 3.8+
* Pip (gerenciador de pacotes Python)

### 1. Clonar o Repositório (Exemplo)

```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd PI4-2025
````

### 2\. Criar e Ativar o Ambiente Virtual

```bash
# Criar ambiente
python -m venv .venv

# Ativar no Windows
.venv\Scripts\activate

# Ativar no Linux/macOS
source .venv/bin/activate
```

### 3\. Instalar Dependências

```bash
pip install -r requirements.txt
# Se não tiver o requirements.txt, instale as principais:
# pip install Flask Flask-SQLAlchemy Flask-Mail Flask-APScheduler Flask-RESTX WeasyPrint
```

### 4\. Configurar Variáveis de Ambiente (Opcional, mas recomendado)

Para a configuração de e-mail e chaves secretas, é recomendado usar variáveis de ambiente ou um arquivo `.env`.

  * **Observação sobre E-mail (Gmail):** Lembre-se de que a variável `MAIL_PASSWORD` deve ser uma **Senha de App** gerada no painel de segurança da sua Conta Google, caso a Verificação em Duas Etapas esteja ativada.

### 5\. Executar a Aplicação

```bash
python run.py
```

A aplicação estará acessível em `http://127.0.0.1:5000/`.

## ✨ Funcionalidades

### A. Interface Web (Frontend/Admin)

| Rota | Descrição |
| :--- | :--- |
| `/reservas` | Gerenciamento de todas as reservas. |
| `/equipamentos`| Cadastro e gestão de brinquedos (equipamentos). |
| `/` | Dashboard / Tela Inicial. |

### B. Notificações e Automação

  * **Confirmação de Reserva:** Envio imediato de e-mail ao cliente após a criação de uma reserva.
  * **Lembrete de Retirada:** Tarefa agendada (via Flask-APScheduler) para enviar e-mails de lembrete 1 dia antes da data de início da reserva, incluindo detalhes para retirada.

### C. Relatórios em PDF

  * **Relatório de Reservas:** Exportação em PDF da lista de reservas (com filtros).
  * **Relatório de Inventário:** Exportação em PDF da lista de equipamentos (com filtros de status).

### D. API Pública (RESTful)

  * **Base URL:** `http://127.0.0.1:5000/api`
  * **Documentação:** `http://127.0.0.1:5000/api/docs` (Swagger UI interativo)

| Endpoint | Método | Descrição |
| :--- | :--- | :--- |
| `/api/equipamentos/` | `GET` | Lista todos os equipamentos. |
| `/api/equipamentos/<id>`| `GET` | Detalha um equipamento específico. |
| *Outros* | *Em desenvolvimento* | *Rotas CRUD (POST, PUT, DELETE) para gestão.* |

## 📝 Contato e Licença

  * **Desenvolvedor(es):** [Seu Nome ou Nomes]
  * **E-mail:** [Seu Email]
  * **Licença:** MIT (Sugestão: Permite o uso e modificação, com atribuição.)