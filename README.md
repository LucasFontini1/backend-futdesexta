# Fut de Sexta — Backend

API REST Django + Django REST Framework do Fut de Sexta. Mantém a estrutura
original `app/` (configuração) e `core/{models,serializers,views}/` (domínios)
dos repositórios de referência do IFC.

## Executar localmente

1. Instale Python compatível e PDM.
2. Rode `pdm install`.
3. Copie `.env.example` para `.env`, configure `DEBUG=true` e uma `SECRET_KEY` de desenvolvimento.
4. Execute `pdm run migrate` e `pdm run dev`.
5. API em `http://127.0.0.1:8000/api/` e documentação em `/api/doc/`.

## Banco, imagens e autenticação

- SQLite em desenvolvimento; Supabase PostgreSQL via `DATABASE_URL` em produção.
- Cloudinary via `CLOUDINARY_URL`, **somente no servidor**. Sem credenciais, uploads ficam locais para desenvolvimento.
- Django mantém o modelo de usuários, hash de senhas e regras de autorização. A API existente usa JWT SimpleJWT com access token curto; não exponha tokens em logs nem salve chaves no repositório.
- As equipes são privadas: todo acesso aos detalhes precisa ser autorizado por objeto no backend.
- Não publique arquivos pessoais nem dumps de banco; imagens de usuários dependem de permissões de acesso e política de privacidade.

## Qualidade

`pdm run check` (Ruff), `pdm run format` (Ruff),
`pdm run test` (testes Django), `python manage.py check --deploy`
(revisão adicional das configurações de produção).
Os testes em CI não substituem testes de integração reais com Supabase e Cloudinary.

## Estrutura

- `app/`: settings, urls, WSGI/ASGI e paginação.
- `core/models/`: entidades e regras estruturais.
- `core/serializers/`: validação e exposição controlada dos dados.
- `core/views/`: endpoints, permissão por objeto e ações.
- `core/migrations/`: evolução do esquema Django.
- `core/tests/`: testes de funcionamento e segurança.
- `http/`: coleção Bruno legada (não usar como especificação do Fut de Sexta).
- `scripts/`: ferramentas auxiliares de desenvolvimento.

## Planejamento

Funcionalidades de peladas, estatísticas por categoria, amistosos e competições
serão integradas por módulos. Não considerar documentação como implementação.
