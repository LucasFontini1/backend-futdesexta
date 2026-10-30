# Fut de Sexta — API Django

Backend do Fut de Sexta: **Django + Django REST Framework + PostgreSQL (Supabase)**, com armazenamento de imagens via **Cloudinary** quando configurado. Mantém a organização original do Instituto Federal Catarinense: `app/` para configuração e `core/models/`, `core/serializers/`, `core/views/`, `core/services/`, `core/migrations/`, `core/tests/` separados por domínio.

> Branch de desenvolvimento em revisão, sem aprovação para produção. Nem todos os serviços externos estão configurados ou verificados.

## Rodar localmente

1. Instale Python 3.12 e dependências: `python -m pip install -r requirements.txt`.
2. Copie `.env.example` como `.env` e configure `DEBUG=true` e uma `SECRET_KEY` segura para desenvolvimento.
3. Execute `python manage.py migrate`.
4. Execute `python manage.py runserver 127.0.0.1:8000`.
5. Documentação OpenAPI em `http://127.0.0.1:8000/api/doc/`.

PDM também é suportado. Antes de usar `pdm install` em ambiente real, atualize o lockfile (`pdm lock`) depois das alterações em `pyproject.toml`; não confie no lock antigo do template.

## Domínios e API

- `/api/registro/`, `/api/token/`, `/api/usuarios/` e `/api/usuarios/me/`: cadastro, login e perfil.
- `/api/conta/`: confirmação de e-mail, recuperação e alteração de senha, solicitação de exclusão.
- `/api/equipes/`, `/api/convites-equipe/`: equipes privadas, convites, elenco, administração e vínculos.
- `/api/partidas/`, `/api/recorrencias/`: peladas, presença, lados, escalações e resultado.
- `/api/estatisticas/`: rankings por modalidade, com total geral.
- `/api/amistosos/`, `/api/competicoes/`, `/api/convites-competicao/`: partidas entre equipes cadastradas e competições.
- `/api/calendario/`, `/api/eventos/`, `/api/notificacoes/`: agenda, eventos e alertas.
- `/api/geocodificar/`, `/api/partidas/<id>/clima/`: endereço e previsão meteorológica.

## Banco e Cloudinary

Configure `DATABASE_URL` com **string de conexão do Supabase PostgreSQL** com SSL. As migrações são mantidas pelo Django, não pelo Supabase Auth; o Django centraliza a autorização. Use `CLOUDINARY_URL` somente no servidor para fotos de perfil, escudos, jogadores, competições e eventos. Nunca exponha uma chave do Cloudinary ou o acesso privilegiado do Supabase no frontend.

Em desenvolvimento, SQLite e sistema de arquivos local são usados por padrão. Testes da CI usam SQLite; portanto **não substituem testes reais de PostgreSQL e Cloudinary**.

## E-mail e push

O cadastro exige confirmação de e-mail. Em desenvolvimento, mensagens são emitidas no console; em produção, configure `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` e `DEFAULT_FROM_EMAIL`. Para web push configure `VAPID_PRIVATE_KEY` e `VAPID_SUBJECT` no servidor. No frontend, somente a chave VAPID **pública**.

Comandos que podem ser agendados por cron/scheduler com permissões restritas:

```bash
python manage.py gerar_peladas --weeks 8
python manage.py lembrar_partidas
python manage.py enviar_push
```

Evite executar os agendamentos em instâncias concorrentes sem um mecanismo de bloqueio distribuído em produção.

## Qualidade e segurança

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py test
ruff check --select F,E --ignore E501 app core
ruff format --check app core
```

Testes contemplam autorização por objeto, convites, vínculos, partidas, placares, campeonatos e recuperação de senha. Antes de publicar, validar cabeçalhos e HTTPS no domínio real, limites de requisição com cache compartilhado, uploads, concorrência real em PostgreSQL e auditoria LGPD.

## Pendências verificáveis

Ainda requerem validação final: suíte ponta a ponta conjunta frontend/backend, integração real com Supabase/Cloudinary/SMTP/push, disponibilidade dos provedores de mapas/clima, configuração de agendador, licença (metadados herdados do template eram conflitantes), escalação de equipes adversárias no editor, revisão jurídica da política e deploy em HTTPS.

Os PRs permanecem abertos. O projeto não deve ser apresentado como 100% concluído sem essas verificações.
