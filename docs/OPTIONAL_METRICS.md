# Estatísticas opcionais — Fut de Sexta

Cada jogador pode receber cartões amarelos, cartões vermelhos, faltas e
defesas. Esses valores **não são obrigatórios**: quando não registrados,
permanecem `null`, e não `0`.

## Endpoints
- `GET /api/partidas/:id/metricas/`: lista os registros da partida para quem tem acesso.
- `POST /api/partidas/:id/metricas/`: salva somente os campos enviados.

Exemplo:
```json
{"player": 17, "saves": 0, "yellow_cards": 1}
```

O jogador deve pertencer à escalação da partida. Somente administradores
autorizados podem registrar informações; nos amistosos cada equipe só edita
as métricas dos próprios jogadores.

O banco garante unicidade por jogador e partida. O endpoint atualiza o
registro existente sem criar duplicatas nem substituir valores omitidos.
Ranking e total geral agregam as métricas somente em partidas finalizadas,
por modalidade (peladas, amistosos e competições). Reservas não são
contabilizados como participantes até entrarem na escalação titular.

## Testes
`python manage.py test core.tests.test_optional_metrics`

Testar com PostgreSQL/Supabase antes de produção para confirmar
concorrência e validar o desempenho de rankings em grandes equipes.
