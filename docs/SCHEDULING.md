# Integridade de horários e conflitos de agendamento

## Problema evitado

Uma equipe não deve aceitar amistoso ou entrar em um confronto de competição
que se sobreponha a outra partida agendada ou em andamento, mesmo quando
aparece como visitante em uma partida compartilhada por duas equipes.

## Regra

O intervalo é semiaberto: `[início, término)`. Assim, uma partida iniciada
exatamente quando outra termina não conflita. Partidas canceladas e finalizadas
não bloqueiam novos agendamentos.

A função `core.services.schedule.assert_teams_available`:

1. Verifica a existência das equipes cadastradas.
2. Bloqueia suas linhas em ordem de ID via `select_for_update()`.
3. Verifica conflitos em partidas da equipe organizadora ou dos lados.
4. Em caso de conflito, retorna HTTP 400 sem criar novas partidas.

Chamar somente dentro de `transaction.atomic()` e manter o bloqueio
até a conclusão da criação do confronto. Em produção, PostgreSQL é necessário
para a proteção concorrente; SQLite não oferece as mesmas garantias de lock.

## Validação

`python manage.py test core.tests.test_schedule_conflicts`

Testes cobrem conflito com pelada interna, horário contíguo permitido,
partida cancelada, aceite de amistoso e criação de confronto de competição.

## Limitação atual

A geração de peladas recorrentes não passa por esse serviço, pois a série
precisa de uma política de conflitos diferente. Implementações futuras devem
definir se a ocorrência deve ser omitida ou marcada para resolução manual.
