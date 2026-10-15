# Desafio Python DIO — API Bancária

[![CI](https://github.com/Silva-D-Romario/Desfio-Python-DIO/actions/workflows/ci.yml/badge.svg)](https://github.com/Silva-D-Romario/Desfio-Python-DIO/actions/workflows/ci.yml)

API REST assíncrona para operações bancárias, desenvolvida como uma evolução autoral dos
desafios da **Formação Python Backend Developer da DIO**. O projeto transforma o exercício de
terminal em uma aplicação backend testável, documentada e preparada para integração contínua.

> O nome `Desfio-Python-DIO` foi mantido conforme definido para o repositório.

## Funcionalidades

- cadastro de usuário com conta bancária automática;
- autenticação por JWT;
- consulta de conta e saldo;
- depósito, saque e transferência entre contas;
- extrato ordenado com identificação da contraparte;
- validação de saldo, valores monetários e duplicidade de cadastro;
- documentação interativa OpenAPI/Swagger;
- testes automatizados, cobertura mínima e análise estática na CI.

## Tecnologias

- Python 3.11+
- FastAPI e Uvicorn
- SQLAlchemy 2 com operações assíncronas
- SQLite com `aiosqlite`
- Pydantic
- PyJWT e Argon2
- Pytest, Coverage e Ruff
- Docker e GitHub Actions

## Arquitetura

```text
src/bank_api/
├── routers/          # endpoints HTTP
├── config.py         # configuração por variáveis de ambiente
├── database.py       # engine e sessões assíncronas
├── dependencies.py   # autenticação e dependências FastAPI
├── models.py         # entidades SQLAlchemy
├── schemas.py        # contratos de entrada e saída
├── security.py       # hash de senha e JWT
├── services.py       # regras de negócio
└── main.py           # inicialização da API
```

## Executar localmente

```bash
git clone https://github.com/Silva-D-Romario/Desfio-Python-DIO.git
cd Desfio-Python-DIO
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn bank_api.main:app --reload
```

Acesse:

- Swagger UI: <http://localhost:8000/docs>
- OpenAPI: <http://localhost:8000/openapi.json>
- Health check: <http://localhost:8000/health>

## Fluxo de uso

Cadastre um usuário:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Romario Silva","email":"romario@example.com","cpf":"12345678901","password":"senha123"}'
```

Obtenha o token (o campo `username` recebe o e-mail):

```bash
curl -X POST http://localhost:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=romario@example.com&password=senha123'
```

Use o token retornado nas operações protegidas:

```bash
curl -X POST http://localhost:8000/transactions/deposit \
  -H 'Authorization: Bearer SEU_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"amount":"150.00"}'
```

## Qualidade

```bash
ruff check .
pytest
```

A pipeline executa lint e testes com cobertura nas versões 3.11, 3.12 e 3.13 do Python.

## Docker

```bash
docker build -t desfio-python-dio .
docker run --rm -p 8000:8000 \
  -e JWT_SECRET='uma-chave-segura' \
  desfio-python-dio
```

## Referência acadêmica

O ponto de partida conceitual foi o repositório oficial
[digitalinnovationone/trilha-python-dio](https://github.com/digitalinnovationone/trilha-python-dio),
especialmente os exercícios de sistema bancário e APIs assíncronas com FastAPI. A arquitetura,
organização, documentação, regras adicionais, testes e automação deste repositório foram
implementados de forma própria para demonstrar competências de backend.

## Licença

Distribuído sob a licença MIT. Consulte [LICENSE](LICENSE).

