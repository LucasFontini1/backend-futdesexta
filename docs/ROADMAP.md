# Fut de Sexta — quadro de desenvolvimento

Este quadro documenta o estágio técnico dos recursos. Ele não substitui o
GitHub Projects V2, cujo quadro interativo ainda precisa ser criado.

## Backlog
- Validar legalmente a política de privacidade e a licença do software.
- Ajustar infraestrutura PostgreSQL/Supabase, Cloudinary, SMTP e Web Push com
  credenciais de teste e verificações de segurança reais.
- Revisar políticas de armazenamento privado e retenção de fotos de jogadores.
- Testes de concorrência em PostgreSQL e testes de carga.

## Todo
- Configurar tarefas agendadas de recorrência, lembretes e notificações push.
- Planejar hospedagem, HTTPS, backups, monitoramento e reversão de migrations.
- Testar comportamento PWA/offline e push em dispositivos reais.

## In Progress
- Integrar alterações dos PRs dependentes de agenda, identidade visual e
  estatísticas opcionais, sem mesclar código não revisado na `main`.

## In Review
- [Backend PR #1](https://github.com/LucasFontini1/backend-futdesexta/pull/1):
  autenticação, equipes privadas, convites, elenco, peladas, partidas,
  escalação, resultados, amistosos, competições, calendário e notificações.
- [Backend PR #11](https://github.com/LucasFontini1/backend-futdesexta/pull/11):
  integridade de agenda e prevenção de conflitos entre equipes.
- [Backend PR #12](https://github.com/LucasFontini1/backend-futdesexta/pull/12):
  cartões, faltas e defesas opcionais com `null` quando não informados.
- [Frontend PR #1](https://github.com/LucasFontini1/frontend-futdesexta/pull/1):
  páginas Vue, sessões, equipes, peladas, competições e módulos conectados à API.
- [Frontend PR #7](https://github.com/LucasFontini1/frontend-futdesexta/pull/7):
  E2E, logos oficiais, favicon e ícones PWA.
- [Frontend PR #8](https://github.com/LucasFontini1/frontend-futdesexta/pull/8):
  telas de métricas opcionais.

## Testing
- Suíte Django, `ruff check`, `ruff format --check`, migrations e
  `makemigrations --check --dry-run`: verificação automática no GitHub Actions.
- Frontend: build Vite, ESLint, Prettier e Playwright com backend de teste.
- Todos os testes de CI usam credenciais falsas e SQLite; execução em serviços
  externos reais **não está concluída**.

## Done
- Definição de stack (Vue 3, Django/DRF, Supabase PostgreSQL e Cloudinary).
- Identidade visual clara/escura incorporada aos ativos do frontend.
- Testes automatizados básicos e CI configurados para as branches de trabalho.

## Requisitos para marcar uma issue como Done
API real, permissão no servidor, persistência, UI conectada, testes
funcionais e de segurança, documentação e revisão. Não confundir
uma compilação bem-sucedida com aprovação para produção.

## GitHub Project
Os itens têm issues e pull requests ligados ao GitHub. A criação e configuração
do quadro visual **GitHub Projects V2** ainda não está disponível pela conexão
atual; não declarar que esse quadro existe até ser confirmado.
