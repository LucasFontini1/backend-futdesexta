# Fut de Sexta — autenticação

Código reconstruído a partir da branch `main` original; nesta fase apenas o **login JWT por e-mail e senha** está no escopo.

## Arquitetura
Mantém Django em `app/` e `core/models/`, `core/serializers/`, `core/views/`. Referência somente de leitura: `Hackaton-2026-IFC/Backend-Hackathon`.

## Rodar localmente
1. Copie `.env.example` para `.env` e gere uma `SECRET_KEY` aleatória.
2. Execute `pdm install` e `pdm migrate`.
3. Execute `pdm run python manage.py createsuperuser` para criar uma conta com e-mail e senha.
4. Execute `pdm dev`.
5. Abra o frontend em `http://localhost:5173`.

## API
- `POST /api/token/` — e-mail e senha; responde access e refresh.
- `POST /api/token/refresh/` — renova access.
- `POST /api/token/verify/` — valida JWT.
- `GET /api/usuarios/me/` — exige Bearer e retorna somente id, nome e e-mail.

Testes: `pdm run python manage.py test core.tests.test_login`.

A tela de login não possui cadastro de usuário, recuperação de senha, equipes nem partidas nesta etapa. Repositórios de referência não foram modificados.
