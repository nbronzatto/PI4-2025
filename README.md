# Sistema de Gestão de Brinquedos para Festas

Desenvolvido com **Flask + SQLite**, criado para **cadastrar, reservar e gerenciar brinquedos infantis de aluguel** para festas e eventos.

## Imagens do Sistema

* Tela Principal  
  ![Tela Principal](/imgs/home.PNG)

* Modelagem Banco de Dados
  ![Modelagem](/imgs/diagrama_db.PNG)

* Reservas  
  ![Reservas](/imgs/reserva.PNG)
  
## Funcionalidades

```mermaid
erDiagram
    reservas {
        int id
        int equipamento_id
        date data_inicio
        date data_fim
        string cliente_nome
        string cliente_contato
        date data_criacao
    }

    equipamentos {
        int id
        string nome
        string descricao
        string status
    }

    user {
        int id
        string username
        string email
    }

    reservas ||--|| equipamentos : "possui"

```
* Cadastro e listagem de brinquedos
* Gestão de reservas (criar, finalizar e excluir)
* Dashboard com estatísticas
* Filtros e buscas avançadas
* Interface responsiva (desktop e mobile)

## Tecnologias

* Backend: Flask (Python)
* Banco de Dados: SQLite
* Frontend: Bootstrap 5 + Jinja2

## Melhorias Futuras

* Autenticação de usuários
* Relatórios em PDF
* Notificações por e-mail
* API REST para integração

