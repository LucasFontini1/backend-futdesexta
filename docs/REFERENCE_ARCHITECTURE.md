# Arquitetura de referência — Backend-Hackathon

Referência somente leitura: https://github.com/Hackaton-2026-IFC/Backend-Hackathon

## Convenções adotadas

- `app/` concentra configurações e roteamento global.
- `core/models/` separa entidades por domínio.
- `core/serializers/` valida payloads e restringe a exposição dos campos.
- `core/views/` contém ViewSets, actions e permissões.
- `core/services/` implementa regras transacionais e processos compartilhados.
- `core/tests/` mantém testes por fluxo e regressão de segurança.
- `core/views/token.py` usa SimpleJWT com serializer customizado e documentação OpenAPI.

## Domínios do Fut de Sexta

Não reutilizar entidades de projetos/tarefas do Hackathon: a aplicação possui
equipes privadas, jogadores, convites, partidas, presenças, recorrências,
escalações, resultados, métricas, amistosos, torneios, eventos e notificações.

## Regras essenciais

- Controle de acesso por equipe em todos os endpoints.
- Membros convidados; ações administrativas exigem cargo de administrador.
- Resultados e estatísticas são registrados pelos administradores.
- Estatísticas por modalidade, com agregação geral sem duplicação.
- Competições só aceitam equipes cadastradas.
- URLs, credenciais e chaves nunca entram no Git.
- Cloudinary para arquivos; PostgreSQL/Supabase para persistência.
- Alterações de banco apenas por migrações incrementais.
- Sessões JWT com access e refresh compatíveis com o frontend.
- Testes de segurança, permissões, concorrência, dados e regressão antes de merge.

## Verificações

`ruff check --select F,E --ignore E501 app core`
`ruff format --check app core`
`python manage.py check`
`python manage.py makemigrations --check --dry-run`
`python manage.py migrate --noinput`
`python manage.py test`

A aprovação dessas verificações não equivale a testes reais com todas as
integrações externas ou a um certificado de prontidão em produção.

## Histórico

A API aceita filtros opcionais `status` e `kind` na listagem de partidas,
sempre limitados às equipes permitidas ao usuário autenticado.
