# Mapa do código do ExplAIner

Este mapa mostra **onde** cada coisa está. O `GUIA_DE_ESTUDO.md` explica **como** e **por quê**.

Os caminhos são relativos à raiz do projeto.

## 1. Funcionalidades → arquivos

| Funcionalidade | Arquivo(s) | Responsabilidade |
|---|---|---|
| Iniciar a aplicação | `backend/app.py` | Cria o Flask (`create_app`), carrega o `.env`, valida a chave de sessão, configura cookie e CORS, registra os Blueprints, bloqueia o painel legado e cria e migra o banco |
| Conexão com o banco | `backend/models/database.py` | Objeto `db` (Flask-SQLAlchemy) compartilhado por todos os models |
| Rotas da área do estudante | `backend/controllers/aprendizado_controller.py` | Recebe o HTTP, confere o login (`rota()`), chama o Service e devolve o JSON |
| Erros de negócio | `backend/services/aprendizado/erros.py` | `ErroDeNegocio(mensagem, status)`, convertido em resposta HTTP pelo `rota()` |
| Regras do jogo | `backend/services/aprendizado/regras.py` | Pontos por dificuldade, penalidade, bônus, fases, escada de dificuldade, foguinho e versão dos termos |
| Cadastro, login, termos, perfil, exclusão | `backend/services/aprendizado/conta_service.py` | `ContaService`: validações, hash de senha, limite de tentativas de login e aceite dos termos |
| Catálogo, gerar desafio, retomada, refazer | `backend/services/aprendizado/desafio_service.py` | `DesafioService`: catálogo, `criar`, `desafio_ativo`, `buscar` e `_criar_revisao` |
| Geração de questões | `backend/services/aprendizado/gerador_questoes.py` | OpenAI (com nova tentativa) ou banco local do próprio tema, sem repetir questões e com alternativas embaralhadas |
| Responder questão | `backend/services/aprendizado/resposta_service.py` | `RespostaService.responder`: valida, corrige, pontua e grava a resposta |
| Concluir fase e reprovação | `backend/services/aprendizado/conclusao_service.py` | `ConclusaoService.concluir`: bônus, regra dos 70% e desfazer a jornada |
| Progresso, ranking, histórico, tempo ativo | `backend/services/aprendizado/progresso_service.py` | `ProgressoService`: resumo do aluno, ranking, histórico e heartbeat |
| Exclusão sem registros órfãos | `backend/services/exclusao.py` | `remover_aluno` e `remover_desafio` apagam os dependentes antes; `_apagar_questoes_sem_uso` limpa as questões que ficaram sem desafio |
| Transações | `backend/repositories/transacao.py` | `Transacao.confirmar()` (commit), `desfazer()` (rollback), `enviar()` (flush) |
| Ranking em SQL puro | `backend/repositories/aluno_repositories.py` | `ranking_topo`, `total_participantes`, `participa_do_ranking` e `quantos_a_frente` com `text()` |
| Respostas | `backend/repositories/resposta_repository.py` | Buscar, listar, adicionar e contar as respostas de um desafio |
| Desafios | `backend/repositories/desafio_repository.py` | `buscar_por_id`, `listar`, `buscar_por_nome`, `listar_do_aluno`, `anteriores_no_tema`, `fase_concluida`, adicionar e remover |
| Questões de um desafio | `backend/repositories/desafio_questao_repository.py` | `ids_questoes` (ordem das bolinhas), `buscar`, `pertence`, `vincular`, `remover`, `questao_em_uso` |
| Questões | `backend/repositories/questao_repository.py` | Buscar, `listar`, `listar_do_desafio`, `enunciados_ja_vistos`, verificação legada |
| Conclusões de fase | `backend/repositories/aluno_desafio_repository.py` | Registro da conclusão, `historico` (30 mais recentes) |
| Temas | `backend/repositories/tema_repository.py` | Catálogo de temas, buscar por id, `listar`, `possui_vinculos`, adicionar e remover |
| Ranking legado | `backend/repositories/ranking_repository.py` | Tabela `Ranking` do painel antigo: buscar, listar, adicionar e remover |
| Atualização de campos | `backend/services/atualizacao.py` | `aplicar_campos` (só altera o que foi enviado) e `converter_data` (texto ISO → `date`), usados pelos services de atualização do painel legado |
| Tabelas | `backend/models/model_*.py` | Uma classe por tabela (seção 4), só com colunas e `to_dict()`; quem grava e consulta é o Repository |
| Esquema para MySQL | `backend/database/create_database.sql` | `CREATE TABLE` com chaves primárias e estrangeiras, `UNIQUE` e índices |
| Tela do estudante | `frontend/estudar.html` | Todas as telas (login, aprender, mapa, ranking, progresso, modais) |
| Comportamento da tela | `frontend/estudar.js` | `api()` (fetch), estado, mapa, questões, conclusão, retomada, ranking e conta |
| Visual | `frontend/estudar.css`, `frontend/style.css` | Tema escuro e claro, mapa, trilha, responsividade; estilos do painel legado |
| Botão "Voltar" | `frontend/voltar.js` | Volta para a página anterior ou para a tela inicial |
| Termos (LGPD) | `frontend/termos-de-uso.html`, `frontend/termo-de-consentimento.html` | Textos dos termos aceitos no cadastro |
| Painel administrativo legado | `frontend/index.html`, `listar.html`, `ler.html`, `atualizar.html`, `deletar.html`, `temas.html`, `questoes.html`, `desafios.html`, `ranking.html` e os `.js` de mesmo nome, `script.js` | CRUD antigo; desligado por padrão |
| Diagramas | `docs/diagrama_classes.*`, `docs/fluxograma_*.*` | Diagrama de classes e os fluxos de entrada e de recuperação de dados |
| Testes | `tests/test_api.py`, `tests/test_banco_local.py` | 38 testes e 48 subtestes (`python -m pytest tests -q`) |
| Dependências | `requirements.txt`, `requirements-dev.txt` | Bibliotecas para rodar; mais o `pytest` para testar |
| Configuração de exemplo | `.env.example` | Variáveis de ambiente sem valores reais |

## 2. Endpoints da área do estudante

Todos estão em `backend/controllers/aprendizado_controller.py`. "Login" indica se o `@rota()` exige um aluno na sessão.

| Método e rota | Função do Controller | Service | Repositories principais | Login |
|---|---|---|---|---|
| `POST /api/auth/register` | `registrar_conta` | `ContaService.registrar` | `AlunoRepository` | não |
| `POST /api/auth/login` | `entrar_conta` | `ContaService.entrar` e `ProgressoService.progresso` | `AlunoRepository` | não |
| `POST /api/auth/logout` | `sair_conta` | — (`session.clear()`) | — | não |
| `DELETE /api/auth/delete-account` | `excluir_propria_conta` | `ContaService.excluir` → `exclusao.remover_aluno` | todos os que apontam para o aluno | sim |
| `POST /api/auth/accept-terms` | `aceitar_termos` | `ContaService.aceitar_termos` | `Transacao` | sim |
| `GET /api/learning/me` | `minha_conta` | `ProgressoService.progresso` | `AlunoDesafioRepository`, `AlunoRepository` | sim |
| `PATCH /api/learning/profile` | `atualizar_perfil` | `ContaService.atualizar_nick` | `Transacao` | sim |
| `GET /api/learning/catalog` | `catalogo_estudo` | `DesafioService.catalogo` | `TemaRepository` | não |
| `GET /api/learning/active-challenge` | `desafio_em_andamento` | `DesafioService.desafio_ativo` | `DesafioRepository`, `DesafioQuestaoRepository`, `RespostaRepository` | sim |
| `POST /api/learning/challenges` | `criar_desafio_jogavel` | `DesafioService.criar` (ou `_criar_revisao`) → `gerar_questoes` | `TemaRepository`, `DesafioRepository`, `QuestaoRepository`, `DesafioQuestaoRepository` | sim |
| `GET /api/learning/challenges/<id>` | `buscar_desafio_jogavel` | `DesafioService.buscar` | `DesafioRepository`, `DesafioQuestaoRepository` | sim |
| `POST /api/learning/challenges/<id>/answer` | `responder_questao` | `RespostaService.responder` | `DesafioRepository`, `QuestaoRepository`, `DesafioQuestaoRepository`, `RespostaRepository` | sim |
| `POST /api/learning/challenges/<id>/complete` | `concluir_desafio` | `ConclusaoService.concluir` | `RespostaRepository`, `AlunoDesafioRepository`, `DesafioRepository` | sim |
| `POST /api/learning/activity` | `registrar_tempo_ativo` | `ProgressoService.registrar_tempo_ativo` | `Transacao` | sim |
| `GET /api/learning/ranking?limite=N` | `ranking_de_estudo` | `ProgressoService.ranking` | `AlunoRepository` (SQL puro) | não |
| `GET /api/learning/history` | `historico_estudo` | `ProgressoService.historico` | `AlunoDesafioRepository` | sim |

## 3. Endpoints do painel legado (desligados por padrão)

Ficam ligados só com `ENABLE_ADMIN_PANEL=1`; sem ele, `bloquear_crud_legado` (em `app.py`) responde 403. Assim como o fluxo do estudante, cada service daqui consulta e grava pelos Repositories e fecha o caso de uso com `Transacao.confirmar()`.

| Controller | Rotas | Services (`backend/services/...`) |
|---|---|---|
| `aluno_controller.py` | `POST/GET /alunos`, `GET/PUT/DELETE /alunos/<id>`, `GET /alunos/ranking` | `aluno/criar_aluno`, `listar_aluno`, `buscar_por_id`, `atualizar_aluno`, `deletar_aluno`, `ranking_dos_alunos` |
| `tema_controller.py` | `POST/GET /temas`, `PUT/DELETE /temas/<id>` | `tema/criar_tema`, `listar_tema`, `atualizar_tema`, `deletar_tema` |
| `questao_controller.py` | `POST/GET /questoes`, `PUT/DELETE /questoes/<id>`, `POST /questoes/<id>/verificar` | `questao/criar_questao`, `listar_questao`, `atualizar_questao`, `deletar_questao`, `verificar_questao` |
| `desafio_controller.py` | `POST/GET /desafio`, `GET /desafio/nome/<nome>`, `PUT/DELETE /desafio/<id>` | `desafio/criar_desafio`, `listar_desafio`, `buscar_por_nome_desafio`, `atualizar_desafio`, `deletar_desafio` |
| `desafio_questao_controller.py` | `POST/DELETE /desafios/<id>/questoes/<id_questao>`, `GET /desafios/<id>/questoes` | `desafio_questao/adicionar_questao_desafio`, `listar_questoes_desafio`, `remover_questao_desafio` |
| `aluno_desafio_controller.py` | `POST /alunos/desafios`, `GET /alunos/<id>/desafios`, `PUT /alunos/<id>/desafios/<id_desafio>` | `aluno_desafio/registrar_aluno_desafio`, `listar_desafios_aluno`, `atualizar_aluno_desafio` |
| `ranking_controller.py` | `POST/GET /ranking`, `PUT/DELETE /ranking/<id>` | `ranking/criar_ranking`, `listar_ranking`, `atualizar_ranking`, `deletar_ranking` |

## 4. Models → tabelas

| Arquivo | Classe | Tabela | Observação |
|---|---|---|---|
| `models/model_aluno.py` | `Aluno` | `Aluno` | Conta, hash da senha, pontos, foguinho, tempo ativo, aceite dos termos |
| `models/model_tema.py` | `Tema` | `Tema` | Matéria e nome |
| `models/model_questao.py` | `Questao` | `Questao` | Alternativas guardadas em JSON; FK para o tema |
| `models/model_desafio.py` | `Desafio` | `desafio` | Fase da jornada; FK para tema e aluno |
| `models/model_desafio_questao.py` | `DesafioQuestao` | `desafio_questao` | Ligação N–N, com chave composta |
| `models/model_aluno_desafio.py` | `AlunoDesafio` | `aluno_desafio` | Conclusão da fase, com chave composta |
| `models/model_aprendizado.py` | `RespostaDesafio` | `resposta_desafio` | `UNIQUE (id_aluno, id_desafio, id_questao)` |
| `models/model_ranking.py` | `Ranking` | `Ranking` | **Legado**: não é usado no ranking atual |

## 5. Os dois fluxos da apresentação

**Entrada de dados: responder uma questão**

```
frontend/estudar.js          clique em #next-question → api('/api/learning/challenges/<id>/answer', POST)
  └► controllers/aprendizado_controller.py   responder_questao()
      └► services/aprendizado/resposta_service.py   RespostaService.responder()
          ├► services/aprendizado/regras.py            PONTOS_POR_DIFICULDADE, penalidade_por_erro, atualizar_sequencia_diaria
          ├► repositories/desafio_repository.py        buscar_por_id
          ├► repositories/questao_repository.py        buscar_por_id
          ├► repositories/desafio_questao_repository.py pertence, ids_questoes
          ├► repositories/resposta_repository.py       buscar, listar, adicionar
          └► repositories/transacao.py                 confirmar()
              └► models/model_aprendizado.py           RespostaDesafio → tabela resposta_desafio
```

**Recuperação de dados: ranking**

```
frontend/estudar.js          atualizarPainel() → api('/api/learning/ranking?limite=5')
  └► controllers/aprendizado_controller.py   ranking_de_estudo()
      └► services/aprendizado/progresso_service.py   ProgressoService.ranking()
          └► repositories/aluno_repositories.py      ranking_topo, total_participantes,
                                                      participa_do_ranking, quantos_a_frente (SQL com text())
              └► tabelas Aluno + resposta_desafio
```

Os fluxogramas desses dois caminhos estão em `docs/fluxograma_entrada_responder_questao.png` e `docs/fluxograma_recuperacao_ranking.png`.
