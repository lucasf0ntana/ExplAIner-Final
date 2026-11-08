# Guia de estudo do ExplAIner

Esta apostila explica o projeto a partir do código real. O código-fonte desta pasta (`ExplAIner_Estudo/`) não tem comentários: os nomes de classes, métodos e variáveis estão em português e esta apostila e o `MAPA_DO_CODIGO.md` explicam o que cada parte faz.

**Ordem sugerida de leitura:**

1. Este guia, capítulos 1 a 3 (visão geral e arquitetura).
2. `backend/app.py`, que mostra como tudo se conecta.
3. `backend/controllers/aprendizado_controller.py`, com as rotas da área do estudante.
4. `backend/services/aprendizado/` (`regras.py`, depois `resposta_service.py` e `progresso_service.py`).
5. `backend/repositories/aluno_repositories.py` (SQL do ranking) e `resposta_repository.py`.
6. `backend/models/`, as tabelas do banco.
7. `frontend/estudar.js`, a tela que chama a API.
8. Os capítulos 6 e 10 deste guia, que trazem os dois fluxos da apresentação.

O `MAPA_DO_CODIGO.md` mostra **onde** cada coisa está; este guia explica **como** e **por quê**.

---

## Capítulo 1 — Visão geral

**Problema:** estudantes do ensino médio perdem tempo procurando um conteúdo bom quando precisam estudar rápido, não entendem bem as respostas genéricas de IA e não conseguem manter uma rotina de estudos.

**Solução:** uma plataforma de estudos **gamificada**. O aluno escolhe matéria, tema, quantidade de questões e dificuldade, e o sistema monta uma **jornada em fases** num mapa, como num jogo. Cada questão é de múltipla escolha, com correção e explicação imediatas. Há pontos, ranking, sequência de dias ("foguinho") e histórico.

**Público-alvo:** estudantes do ensino médio.

**Como a plataforma funciona, do ponto de vista do aluno:**

1. Cria a conta, aceitando os Termos de Uso e o Termo de Consentimento, e entra.
2. Em **Aprender**, escolhe matéria, tema, quantidade (5, 10, 15 ou 20) e dificuldade inicial.
3. O sistema gera a fase 1 e abre o **mapa**: cada bolinha é uma questão, respondida em ordem.
4. Ao responder, vê se acertou, a alternativa correta, a explicação e os pontos. A bolinha ganha ✓ ou ✗.
5. Com tudo respondido, conclui a fase, recebe os bônus e segue para a próxima fase, que vem mais difícil.
6. Pode sair a qualquer momento e voltar depois: **Continuar desafio** e **Continuar jornada**.
7. Acompanha a evolução em **Ranking** e **Meu progresso**, e pode **Refazer** fases antigas (sem pontos).

**De onde vêm as questões:** da API da OpenAI, com a chave em `OPENAI_API_KEY` (variável de ambiente, nunca no código). A IA cria questões novas para o tema e a dificuldade escolhidos. Se ela falhar duas vezes seguidas, os temas que têm **banco local** em `gerador_questoes.py` (Corpo humano, Equações do 1º grau, Figuras de linguagem, Sistema solar e Brasil Colônia) usam esse banco; os outros mostram uma mensagem pedindo para tentar de novo.

---

## Capítulo 2 — Estrutura do projeto

```
ExplAIner/
├── backend/
│   ├── app.py              → cria a aplicação Flask e liga tudo
│   ├── controllers/        → rotas HTTP (recebem a requisição e devolvem JSON)
│   ├── services/           → regras de negócio e casos de uso
│   │   └── aprendizado/    → tudo da área do estudante (o "jogo")
│   ├── repositories/       → acesso ao banco (ORM e SQL puro)
│   ├── models/             → classes que representam as tabelas
│   └── database/create_database.sql → esquema para MySQL
├── frontend/               → HTML, CSS e JavaScript
│   ├── estudar.html/.js/.css → área do estudante (página única)
│   ├── voltar.js           → botão "Voltar" de todas as páginas
│   ├── termos-de-uso.html, termo-de-consentimento.html
│   └── index.html, listar.html, temas.html... → painel administrativo legado (CRUD)
├── docs/                   → diagrama de classes e fluxogramas
├── tests/                  → testes automatizados
└── requirements.txt        → bibliotecas Python necessárias
```

| Camada | Responsabilidade | Exemplo no projeto |
|---|---|---|
| Frontend | Mostrar a tela, capturar cliques e chamar a API | `estudar.js` → `api('/api/learning/ranking')` |
| Controller | Receber o HTTP e devolver o JSON | `aprendizado_controller.responder_questao` |
| Service | Aplicar as regras e coordenar o caso de uso | `RespostaService.responder` |
| Repository | Consultar e gravar no banco | `RespostaRepository.adicionar` |
| Model | Representar uma tabela | `RespostaDesafio` → tabela `resposta_desafio` |

**Dois "mundos" no backend:**

- **Área do estudante (o sistema atual):** `aprendizado_controller.py` e `services/aprendizado/`. É o que a demonstração mostra.
- **Painel administrativo legado:** os outros 7 controllers e os services de `aluno/`, `tema/`, `questao/`... São telas de CRUD puro, sem login nem perfis, e por isso **ficam desligadas por padrão** (capítulo 13). Elas servem como exemplo de CRUD com ORM.

---

## Capítulo 3 — Arquitetura

O caminho de toda requisição é:

```
Frontend (estudar.js) ──fetch/JSON──► Controller ──► Service ──► Repository ──► Model / Banco
         ▲                                                                         │
         └──────────────────────── resposta JSON ◄─────────────────────────────────┘
```

**Por que separar em camadas:**

- **Controller** só conhece HTTP (URL, método, JSON, status). Se um dia a API mudar de formato, as regras não mudam.
- **Service** concentra as **regras de negócio**: "erro tira 25%", "fase 2 só depois da fase 1", "70% de erros reprova". Ficam num lugar só, fáceis de achar, testar e explicar.
- **Repository** concentra o **acesso ao banco**. O Service pede "a resposta desta questão" sem saber se a consulta é ORM ou SQL.
- **Model** descreve as tabelas (colunas, chaves) e é usado pelo ORM para gerar o SQL.

**Exemplo real (trocar o nick):**

1. `estudar.js`: o formulário `profile-form` chama `api('/api/learning/profile', { method: 'PATCH', body: { nick } })`.
2. `aprendizado_controller.atualizar_perfil`: o decorador `@rota()` confere o login e a função chama `ContaService().atualizar_nick(aluno, nick)`.
3. `ContaService.atualizar_nick`: valida o tamanho (1 a 40 caracteres) e altera `aluno.nick`.
4. `Transacao.confirmar()` (em `repositories/transacao.py`) faz o `commit`, e o SQLAlchemy gera `UPDATE Aluno SET nick = ? WHERE id_aluno = ?`.
5. O controller devolve `{"aluno": {...}}`, e o JS atualiza a tela.

**Como os erros atravessam as camadas:** o Service levanta `ErroDeNegocio("mensagem", status)` (em `services/aprendizado/erros.py`). O decorador `rota()` do controller captura o erro e responde `{"erro": "mensagem"}` com o status. No JS, a função `api()` transforma qualquer status que não seja 2xx num `Error` que a tela mostra como aviso.

---

## Capítulo 4 — Cadastro e autenticação

### Cadastro: `POST /api/auth/register`

1. `estudar.js`, no evento `submit` do `register-form`: lê os campos com `FormData` e envia `aceite_termos` como `true` ou `false`.
2. `registrar_conta` (controller) chama `ContaService.registrar(dados)`.
3. Validações, nesta ordem:
   - nome, e-mail e senha são obrigatórios;
   - o e-mail precisa ter formato válido (expressão regular);
   - a senha precisa de pelo menos 8 caracteres;
   - o nome pode ter até 100 caracteres e o nick até 40;
   - o aceite dos termos precisa ser exatamente `true`;
   - o e-mail não pode estar cadastrado (senão, **409**);
   - a data de nascimento, se vier, precisa estar no formato `AAAA-MM-DD`.
4. Cria o `Aluno` com `senha=generate_password_hash(senha)`, registra o aceite (`_registrar_aceite`) e grava com `AlunoRepository.adicionar` e depois `Transacao.confirmar()`.
5. O controller chama `_iniciar_sessao(aluno)` e responde **201**: o aluno já entra logado.

### Hash de senha

Nunca guardamos a senha, só o **hash** gerado pelo Werkzeug, no formato `scrypt:...$sal$hash`:

- **Sal aleatório:** cada hash leva um "sal" sorteado, então duas pessoas com a mesma senha têm hashes diferentes.
- **Sem volta:** não dá para descobrir a senha a partir do hash.
- **Conferência:** `check_password_hash` recalcula o hash da senha digitada com o mesmo sal e compara os dois.
- **Contas antigas:** se alguma ainda tiver senha em texto puro, ela entra normalmente e o login a converte para hash (`senha_confere` e `ContaService.entrar`).

### Login: `POST /api/auth/login`

1. **Bloqueio por tentativas:** 5 erros para o mesmo e-mail e IP, ou 20 erros do mesmo IP, em 15 minutos, bloqueiam o login. A resposta é **429**, com o cabeçalho `Retry-After`.
2. **Busca e conferência:** o Service busca o aluno pelo e-mail e confere a senha. A mensagem de erro é a mesma para "e-mail inexistente" e "senha errada".
3. **Mesmo tempo de resposta:** se o e-mail não existe, o Service confere a senha contra um hash fictício (`_HASH_FICTICIO`), para a resposta demorar o mesmo e não revelar quais e-mails têm conta.
4. **Sucesso:** a sessão é iniciada e a resposta traz `{aluno, progresso}`.

### Sessão

- **O que é:** a sessão do Flask é um **cookie assinado** com a `FLASK_SECRET_KEY`. Ele guarda `aluno_id`, e o navegador o envia em toda requisição.
- **Como o backend identifica o aluno:** `aluno_logado()` lê esse id. É assim que o backend sabe quem está chamando.
- **Proteções do cookie** (em `app.py`):
  - `HttpOnly`: o JavaScript não lê o cookie;
  - `SameSite=Lax`: o cookie não vai em POSTs vindos de outros sites;
  - `Secure`: só trafega por HTTPS, quando `COOKIE_SECURE=1`.
- **Logout:** `POST /api/auth/logout` faz `session.clear()`.

### Aceite dos termos (LGPD)

- **No cadastro:** caixa obrigatória com links para as duas páginas dos termos. O servidor também recusa o cadastro sem `aceite_termos: true`.
- **Registro no banco:** colunas `termos_aceitos_em` (data e hora em UTC) e `versao_termos` (`"1.0"`) no `Aluno`.
- **Contas antigas:** `to_dict()` informa `precisa_aceitar_termos`. Nesse caso o JS abre o modal (`pedirAceiteDosTermos`). Aceitar chama `POST /api/auth/accept-terms`; recusar encerra a sessão.
- **Revogação:** feita pela exclusão da conta (`DELETE /api/auth/delete-account`, que exige a senha).

---

## Capítulo 5 — Geração de desafios

### No frontend

1. **Catálogo:** `GET /api/learning/catalog` traz as matérias e os temas. `montarSelectMaterias()` e `atualizarSelectTemas()` preenchem as listas.
2. **Preview:** `atualizarPreviewPontos()` mostra quantos pontos a fase pode valer e quantas fases a jornada terá.
3. **Confirmação:** ao enviar o `challenge-form`, se já existir um desafio em andamento, o app pede confirmação, porque o servidor vai descartá-lo.
4. **Pedido:** `gerarNovoDesafio()` envia `POST /api/learning/challenges` com `{id_tema, quantidade_questoes, dificuldade, fase_jornada: 1, dificuldade_base}`.

### No backend: `DesafioService.criar`

1. **Validação:** quantidade ∈ {5, 10, 15, 20}, dificuldade reconhecida (`normalizar_dificuldade`) e tema existente.
2. **Fase:** o pedido só vale se a fase anterior do mesmo tema foi concluída (`DesafioRepository.fase_concluida`); senão, volta para a fase 1.
3. **Dificuldade:** é recalculada pela fase real (`dificuldade_da_fase`).
4. **Preparação:**
   - busca os enunciados já vistos (`QuestaoRepository.enunciados_ja_vistos`);
   - apaga o desafio normal em andamento;
   - chama `gerar_questoes(...)`.
5. **Gravação:** cria o `Desafio`, cada `Questao` e cada vínculo `DesafioQuestao`, e chama `Transacao.confirmar()`.
6. **Resposta (201):** traz `{desafio, tema, origem_questoes, aviso, questoes}`. As questões vão **sem a alternativa correta** (`serializar_questao_para_jogo`).

**Refazer:** a mesma rota com `refazer: true` e `refazer_de: <id>` desvia para `_criar_revisao`. Ela só aceita desafios que o aluno já concluiu e cria uma tentativa nova com as **mesmas questões**, sem gerar outras. O nome começa com o prefixo de revisão, e `eh_revisao()` faz essas tentativas valerem 0 pontos.

### O gerador: `gerador_questoes.py`

- **Ordem de tentativa:** `gerar_questoes()` tenta primeiro `_gerar_com_openai`, que faz até **duas chamadas** à IA (devolve `None` sem chave). Se a IA falhar, o erro técnico vai só para o log do servidor e entra `_gerar_local`.
- **Escolha no banco local:**
  1. Procura um **banco temático** cujo trecho esteja no nome do tema (ex.: `"sistema solar"`).
  2. Se não houver, recusa, para nunca entregar pergunta de outro assunto.
  3. Prioriza questões que o aluno **ainda não viu**.
  4. **Embaralha as alternativas** e recalcula a letra correta.
- **Sem banco possível:** se a IA falhar e o tema não tiver banco local, o desafio não é criado e o aluno recebe **502** com "Não foi possível gerar as questões agora. Tente novamente em instantes.".

---

## Capítulo 6 — Responder questão (fluxo de entrada de dados)

`POST /api/learning/challenges/<id>/answer` (fluxograma: `docs/fluxograma_entrada_responder_questao.png`)

### 1. Frontend (`frontend/estudar.js`)

- **Abrir a questão:** o clique na bolinha atual do mapa chama `abrirQuestaoDoMapa()`, que chama `mostrarQuestaoAtual()`. Esta monta as 4 alternativas como botões.
- **Escolher:** clicar numa alternativa chama `selecionarAlternativa(letra)`.
- **Enviar:** o clique no botão `next-question` faz `api('/api/learning/challenges/<id>/answer', { method: 'POST', body: { id_questao, alternativa, segundos_gastos } })`. O tempo é medido com `Date.now()` desde a abertura da questão.

### 2. Controller (`backend/controllers/aprendizado_controller.py`)

`responder_questao(aluno, id_desafio)`:

- o `@rota()` garante o login (401 se não houver);
- `<int:id_desafio>` vem da URL;
- chama `RespostaService().responder(aluno, id_desafio, _dados())` e devolve o resultado com `jsonify`.

### 3. Service (`backend/services/aprendizado/resposta_service.py`)

1. **Valida o formato:** ids numéricos, tempo entre 0 e 3600 s e alternativa A, B, C ou D (senão, **400**).
2. **Confere a posse:**
   - `DesafioRepository.buscar_por_id`;
   - `QuestaoRepository.buscar_por_id`;
   - `DesafioQuestaoRepository.pertence`.
   O desafio precisa ser do aluno e a questão precisa estar nele (senão, **404**).
3. **Já respondida?** `RespostaRepository.buscar`. Se sim, devolve o resultado salvo, sem pontos novos.
4. **Ordem:**
   - `DesafioQuestaoRepository.ids_questoes` dá a ordem das bolinhas;
   - `RespostaRepository.listar` dá as já respondidas.
   Se existe alguma anterior sem resposta, devolve **409**.
5. **Corrige e calcula** com `regras.py`:
   - acerto: `PONTOS_POR_DIFICULDADE`;
   - erro: `penalidade_por_erro`, sem deixar o total negativo;
   - revisão: 0.
6. **Monta o Model:** `RespostaDesafio(...)` e `RespostaRepository.adicionar(...)`.
7. **Atualiza o aluno:** `aluno.pontos` e o foguinho (`atualizar_sequencia_diaria`).
8. **Grava:** `Transacao.confirmar()` faz um único commit com resposta, pontos e foguinho. Se a questão foi respondida ao mesmo tempo em outra aba, a restrição UNIQUE do banco recusa: rollback e **409**.
9. **Responde:** `{correta, alternativa_correta, explicacao, pontos_ganhos, pontos_totais}`.

### 4. Model e banco

`RespostaDesafio` vira uma linha na tabela `resposta_desafio`, e o `Aluno` recebe um `UPDATE` nos pontos.

### 5. Volta ao frontend

- **Alternativas:** a certa fica verde e a escolhida errada fica vermelha.
- **Feedback:** aparecem a explicação e os pontos.
- **Estado:** `state.resultadoQuestoes` guarda se acertou.
- **Mapa:** `renderizarMapaDesafio()` marca a bolinha com ✓ ou ✗ e libera a próxima.

---

## Capítulo 7 — Sistema de pontos

Valores definidos em `backend/services/aprendizado/regras.py`:

| Situação | Pontos |
|---|---|
| Acerto em Fácil / Médio / Difícil | +10 / +15 / +20 |
| Erro | −25% do valor do acerto, arredondado para cima: −3 / −4 / −5 |
| Fase perfeita (acertou todas) | +25 |
| Concluir uma fase | +10 |
| Concluir a última fase da jornada | +50 |
| Revisão ("Refazer") | 0 em tudo (nem respostas nem bônus) |

**Como a penalidade é calculada:** `(ganho + 3) // 4`. O `//` é a divisão inteira.

- Fácil: (10 + 3) // 4 = **3**
- Médio: (15 + 3) // 4 = **4**
- Difícil: (20 + 3) // 4 = **5**

**O total nunca fica negativo:** o erro tira `min(penalidade, pontos_atuais)`. Um aluno com 2 pontos que erra uma questão Média perde só 2.

**Exemplo de uma jornada**, com 5 questões por fase, base Fácil (5 fases):

- **Fase 1 (Fácil):** 5 acertos = 50, mais 25 (perfeita) e 10 (conclusão) = **85**.
- **Fase 2 (Médio):** 4 acertos e 1 erro = 60 − 4 = 56, mais 10 = **66**.
- **Fase 3 (Difícil):** 3 acertos e 2 erros = 60 − 10 = 50, mais 10 = **60**.
- **Fases 4 e 5 (Difícil):** seguem a mesma regra. Na fase 5, se a jornada não for reprovada, entram também os **+50** de jornada completa.

O registro de cada fase (`aluno_desafio.pontuacao_obtida`) guarda os pontos das respostas mais os bônus.

---

## Capítulo 8 — Progressão e conclusão

**Quantidade de fases** (`fases_da_jornada`): 5 questões → 5 fases; 10 → 4; 15 → 3; 20 → 2.

**Dificuldade crescente** (`dificuldade_da_fase`), sobe um degrau por fase com teto em Difícil:

| Base | Fase 1 | Fase 2 | Fase 3+ |
|---|---|---|---|
| Fácil | Fácil | Médio | Difícil |
| Médio | Médio | Difícil | Difícil |
| Difícil | Difícil | Difícil | Difícil |

Na tela aparece "Médio", mas o banco guarda `Normal`. A conversão fica em `regras.DIFICULDADES` (backend) e em `rotuloDificuldade` (frontend).

### Concluir a fase: `POST /api/learning/challenges/<id>/complete` (`ConclusaoService.concluir`)

1. **Pré-condições:** o desafio é do aluno e todas as questões foram respondidas (senão, 400).
2. **Já concluída?** Devolve o resultado com `ja_concluido`, sem pagar bônus de novo.
3. **Última fase:** monta a cadeia de fases da jornada (`_cadeia_da_jornada`) e soma os erros de **todas** elas.
4. **Reprovação:** com `erradas × 100 ≥ 70 × total`, a jornada é reprovada.
   - `_reprovar_jornada` apaga as fases e as revisões delas e tira os pontos que a jornada rendeu.
   - A resposta traz `reprovado: true`.
   - Exemplo: 4 fases × 10 questões = 40 respostas. Com 28 erros, 2800 ≥ 2800 e a jornada **reprova**; com 27 erros, ela é aprovada.
5. **Aprovação:** aplica os bônus, marca `aluno_desafio.concluido = True` e grava tudo.

### Próxima fase

- **Pedido do frontend:** `seguirParaProximaFase()` chama `criarProximoDesafio()` com `faseNaJornada + 1`.
- **Conferência no servidor:** o servidor só aceita se a fase anterior está concluída (`fase_concluida`), então o aluno não consegue pular fases.

---

## Capítulo 9 — Retomada

Tudo o que é necessário para retomar está **no banco**, não no navegador. Por isso a retomada funciona depois de recarregar a página e também em outro dispositivo.

**Ao abrir o app:**

1. `restaurarSessao()` chama `GET /api/learning/me`. Se a sessão ainda vale, o aluno entra direto.
2. `atualizarBotoesDesafio()` chama, ao mesmo tempo, `GET /api/learning/active-challenge` e `GET /api/learning/history`.

**"Continuar desafio":**

- `DesafioService.desafio_ativo` devolve o desafio normal mais recente ainda não concluído, junto com:
  - as questões;
  - `respondidas` (a letra escolhida em cada uma);
  - `acertos` (se acertou ou errou);
  - `todas_respondidas`.
- `continuarDesafioSalvo()` busca o desafio (`GET /api/learning/challenges/<id>`) e `iniciarEstadoDesafio()` remonta o mapa: bolinhas com ✓ e ✗ e a próxima questão liberada.
- Se tudo já foi respondido mas a fase não foi concluída, o botão vira **"Concluir fase N"** e o rodapé do mapa oferece **"Concluir fase ✓"**.

**"Continuar jornada · Fase N/T":** quando não há desafio em andamento, mas a última fase concluída ainda tem próxima.

- `proximaFasePendente()` usa o histórico do servidor para saber tema, quantidade e fase.
- A dificuldade inicial vem do `localStorage`, se existir.
- Se não existir (outro dispositivo), `dificuldadeBaseDaFase()` reconstrói a dificuldade inicial. Isso dá a mesma próxima dificuldade, porque a escada sobe sempre um degrau por fase.

O `localStorage` é só uma conveniência. A fonte da verdade é o banco.

---

## Capítulo 10 — Ranking (fluxo de recuperação de dados)

`GET /api/learning/ranking?limite=5` (fluxograma: `docs/fluxograma_recuperacao_ranking.png`)

1. **Frontend:** `atualizarPainel()` faz `api('/api/learning/ranking?limite=5')`. Quando a aba Ranking está aberta, o limite passa para 100.
2. **Controller:** `ranking_de_estudo(aluno)` lê `limite` da URL com `request.args.get("limite", default=20, type=int)`. Aqui o login não é exigido, então o aluno pode vir `None`.
3. **Service:** `ProgressoService.ranking(aluno_atual, limite)`:
   - limita o valor entre 1 e 100;
   - pede o topo ao Repository;
   - numera as posições (1, 2, 3...) e escolhe o nome exibido (nick ou, na falta dele, o nome);
   - se o aluno logado não está no topo, pede ao Repository quantos estão à frente dele e soma 1.
4. **Repository** (`AlunoRepository`), em **SQL puro** com `text()`:

   ```sql
   SELECT a.id_aluno, a.nome, a.nick, COALESCE(a.pontos, 0) AS pontos,
          a.sequencia_atual, a.foguinho, a.minutos_ativos
   FROM Aluno a
   WHERE a.id_aluno IN (SELECT DISTINCT r.id_aluno FROM resposta_desafio r)
   ORDER BY COALESCE(a.pontos, 0) DESC, a.nome ASC, a.id_aluno ASC
   LIMIT :limite
   ```

   - **Participantes:** só entra quem já respondeu alguma questão (`IN (...)`).
   - **Ordem:** pontos do maior para o menor; empate pelo nome; depois pelo id.
   - **`:limite` é um parâmetro:** o valor vai separado do SQL, o que impede *SQL injection*.
   - **Outras consultas:** `total_participantes()` e `quantos_a_frente()` usam `COUNT(*)` com a mesma ordem.
5. **Resposta:** `{itens: [{posicao, id_aluno, nick, pontos, sequencia_atual, minutos_ativos}], posicao_usuario, total_alunos}`. No JS, `renderizarRankingPreview()` e `renderizarTabelaRanking()` montam as linhas com `textContent`.

**Por que o acesso ao banco fica no Repository:** o Service decide "quem aparece e em que ordem mostrar"; o Repository sabe "como buscar isso no banco". Se a consulta mudar (índice, outro banco), o Service não muda. Além disso, a rubrica pede o SQL nessa camada, e o `AlunoRepository` é o exemplo.

**A tabela `Ranking` não é usada aqui:** ela é legada e só existe para o painel administrativo. O ranking do jogo é calculado pelos **pontos do aluno**.

---

## Capítulo 11 — Banco de dados

**Diagrama:** `docs/diagrama_classes.png` (o código-fonte está em `docs/diagrama_classes.puml`).

| Classe (tabela) | O que guarda | Chave primária | Chaves estrangeiras |
|---|---|---|---|
| `Aluno` (`Aluno`) | conta, hash da senha, pontos, foguinho, tempo ativo, aceite dos termos | `id_aluno` | — |
| `Tema` (`Tema`) | matéria e nome do tema | `id_tema` | — |
| `Questao` (`Questao`) | enunciado, alternativas (JSON), letra correta, explicação | `id_questao` | `id_tema → Tema` |
| `Desafio` (`desafio`) | uma fase: dificuldade, quantidade, nível no mapa, origem | `id_desafio` | `id_tema → Tema`, `id_aluno → Aluno` |
| `DesafioQuestao` (`desafio_questao`) | quais questões estão em cada desafio | (`id_desafio`, `id_questao`) | as duas colunas |
| `AlunoDesafio` (`aluno_desafio`) | conclusão de uma fase: data, pontos, concluído | (`id_aluno`, `id_desafio`) | as duas colunas |
| `RespostaDesafio` (`resposta_desafio`) | cada resposta: letra, acertou, pontos, tempo | `id_resposta` | `id_aluno`, `id_desafio`, `id_questao` |
| `Ranking` (`Ranking`) — **legado** | classificação manual do painel antigo | `id_ranking` | `id_aluno → Aluno` |

**Relacionamentos (cardinalidades do diagrama):**

- **Tema → Questao:** 1 → 0..\*. Toda questão tem tema.
- **Tema → Desafio:** 0..1 → 0..\*. O tema é opcional por causa dos desafios do painel antigo.
- **Aluno → Desafio:** 0..1 → 0..\*. O dono do desafio.
- **Desafio ↔ Questao:** N–N, pela tabela de ligação `desafio_questao`. O "Refazer" reaproveita as mesmas questões.
- **Aluno → AlunoDesafio e Desafio → AlunoDesafio:** 1 → 0..\*.
- **Aluno, Desafio e Questao → RespostaDesafio:** 1 → 0..\* cada.

**Conceitos:**

- **Chave primária:** identifica a linha. Pode ser **composta**, formada por duas colunas.
- **Chave estrangeira:** obriga a coluna a apontar para uma linha existente de outra tabela. No Model, é `db.ForeignKey("Tema.id_tema")`.
- **Restrições:**
  - `UNIQUE` no e-mail do aluno;
  - `UNIQUE (id_aluno, id_desafio, id_questao)` na `resposta_desafio`, que impede responder a mesma questão duas vezes;
  - índices em `id_aluno` e `id_desafio` para buscas rápidas.
- **Relacionamentos no código:** os models declaram as chaves estrangeiras, mas não usam `db.relationship`. As ligações são consultadas nos Repositories com `filter_by` e `join` (ex.: `DesafioRepository.fase_concluida`).
- **ORM e SQL:** o ORM (SQLAlchemy) gera o SQL a partir das classes. O `create_database.sql` mostra o mesmo esquema em SQL puro, para MySQL. Com SQLite, o `app.py` cria tudo sozinho (`create_all`) e acrescenta colunas novas em bancos antigos (`_migrar_schema_sqlite`).

---

## Capítulo 12 — Frontend e API

**Os três arquivos:**

- **`estudar.html`:** a estrutura. Todas as telas existem na página, e o atributo `hidden` esconde as que não estão em uso.
- **`estudar.css`:** o visual. Usa variáveis de cor em `:root`, o tema claro com `body.theme-light`, estados por classe (`.node-wrong`, `.is-done`) e `@media` para telas menores.
- **`estudar.js`:** o comportamento. Responde aos eventos, chama a API e atualiza a tela.

**Como uma chamada funciona:**

```js
const dados = await api('/api/learning/challenges', {
  method: 'POST',
  body: { id_tema: 3, quantidade_questoes: 5, dificuldade: 'facil', fase_jornada: 1 },
});
```

- **`api()` monta e envia:** o `fetch` leva o cabeçalho `Content-Type: application/json`, o corpo em texto (`JSON.stringify`) e o cookie de sessão (`credentials: 'same-origin'`).
- **`await` espera sem travar:** a resposta é aguardada enquanto a página continua respondendo.
- **Tratamento da resposta:** em caso de sucesso, `api()` devolve o objeto JS já convertido. Em erro (4xx/5xx), lança um `Error` com a mensagem do servidor, e quem chamou usa `try/catch`.

**JSON** é o formato de texto usado nos dois sentidos: `{"correta": true, "pontos_ganhos": 15}`.

**Eventos:** `addEventListener('click' | 'submit' | 'change', função)`. Nos formulários, `evento.preventDefault()` evita o recarregamento da página.

**Exibir dados com segurança:** a área do estudante usa `textContent`, que trata o conteúdo como texto e não como HTML. As páginas do painel antigo passam os dados por `esc()` antes de usar `innerHTML`. As duas formas evitam XSS.

**Atualização do mapa:** `renderizarMapaDesafio()`:

- calcula a posição das bolinhas;
- desenha a trilha com `desenharTrilha()`, usando só elementos HTML, sem SVG nem canvas: pílulas arredondadas giradas com `rotate()`;
- cria um `<button>` por questão com o estado: ✓, ✗, atual ou bloqueada.

**Frontend separado da API, mesmo servidor:** o Flask entrega os arquivos de `frontend/` e responde às rotas `/api/...` em JSON. Para mostrar isso na apresentação, abra o **F12**, aba **Rede**, e veja as chamadas `fetch` e as respostas em JSON.

---

## Capítulo 13 — Segurança e privacidade

| Medida | Onde | Por quê |
|---|---|---|
| Senha só como hash | `ContaService.registrar` | Se o banco vazar, as senhas não aparecem |
| Limite de tentativas de login | `conta_service.py` | Impede adivinhar senhas por força bruta (429) |
| Mesmo tempo de resposta no login | `_HASH_FICTICIO` | Não revela quais e-mails têm conta |
| Chave de sessão forte obrigatória | `app.chave_valida` | Com a chave de exemplo, alguém forjaria o cookie e entraria como outro aluno |
| Cookie `HttpOnly`, `SameSite=Lax`, `Secure` | `app.py` | Dificulta roubo do cookie e requisições forjadas de outros sites |
| Painel administrativo legado desligado | `bloquear_crud_legado` | Ele não tem login nem perfis: qualquer um poderia alterar pontos, apagar contas ou ler o gabarito |
| CORS só para origens configuradas | `CORS_ORIGINS` | Outros sites não conseguem chamar a API pelo navegador |
| Gabarito escondido até responder | `serializar_questao_para_jogo` | Ninguém lê a resposta certa no F12 antes de responder |
| Desafio só do próprio aluno | `desafio_do_aluno`, `RespostaService` | Ninguém responde ou consulta desafios de outra pessoa (404) |
| Ordem obrigatória e fase validada no servidor | `RespostaService`, `DesafioService.criar` | O aluno não consegue pular questões nem fases mexendo no navegador |
| Tempo ativo não inflável | `ProgressoService.registrar_tempo_ativo` | Chamadas repetidas não aumentam o tempo do ranking |
| Exclusão de conta exige senha | `ContaService.excluir` | Evita exclusão por outra pessoa com o computador aberto |
| Exclusões em cascata pelo código | `services/exclusao.py` | Não sobram registros órfãos contando no ranking |
| Aceite dos termos registrado | `Aluno.termos_aceitos_em` e `versao_termos` | Exigência da LGPD; revogação pela exclusão da conta |
| Saída protegida contra XSS | `textContent`, `esc()` | Um nick malicioso não executa código na página |
| `.env` e banco fora do GitHub | `.gitignore` | A chave secreta e os dados das contas não são publicados |

**Limitações honestas:**

- O limite de login fica na memória do processo: ele zera se o servidor reiniciar.
- Não há token CSRF. A proteção vem do `SameSite=Lax`.
- O painel legado continua sem perfis de administrador e por isso permanece desligado.

---

## Capítulo 14 — Testes

**Como executar:**

```bash
pip install -r requirements-dev.txt
python -m pytest tests -q
```

Resultado atual: **38 testes e 48 subtestes passando**.

**Como funcionam:**

- **Requisições simuladas:** `app.test_client()` faz requisições sem abrir navegador nem servidor.
- **Banco temporário:** um SQLite criado só para os testes. O banco real não é tocado.
- **Sem IA:** os testes rodam sem chave, com temas que têm banco local; a chamada à IA é simulada.

| Classe em `tests/test_api.py` | O que verifica |
|---|---|
| `TestSeguranca` | Painel legado bloqueado (403), CORS fechado, login exigido e desafio de outra conta (404) |
| `TestContas` | Cadastro, e-mail repetido (409), senha curta (400), logout e login |
| `TestJogo` | Gabarito escondido, ordem obrigatória, resposta repetida e bônus pago uma vez só |
| `TestProgressaoDeDificuldade` | Escada de dificuldade nas 3 bases e fase "forjada" que volta para a 1 |
| `TestReprovacaoDaJornada` | Errar tudo reprova a jornada, zera os pontos e apaga as fases |
| `TestAceiteDosTermos` | Cadastro sem aceite é recusado, aceite registrado e contas antigas aceitando depois |
| `TestRetomada` | Retomar pela metade, concluir depois, próxima fase liberada e acertos na retomada |
| `TestCorrecoesDaAuditoria` | Chave de sessão, limite de login, tempo ativo, exclusões sem órfãos, posição no ranking e outros |

`tests/test_banco_local.py` confere que, sem IA, cada tema recebe só questões do próprio assunto (ou é recusado), que a IA tenta de novo quando a primeira chamada falha, que a falha vira uma mensagem amigável, que as questões estão bem formadas e que o embaralhamento mantém a resposta certa.

---

## Capítulo 15 — Preparação para a apresentação: perguntas e respostas

**1. O que é o Flask e qual é o papel dele no projeto?**
É um framework web para Python. Ele recebe as requisições HTTP, encaminha cada uma para a função da rota (`@aprendizado_controller.post(...)`) e devolve a resposta. Também entrega os arquivos do frontend. Tudo começa em `create_app()`, no `app.py`.

**2. O que é uma API REST e como o projeto a usa?**
É uma API em que os recursos são acessados por URLs, e os métodos HTTP dizem a ação. No projeto: `GET /api/learning/ranking` busca, `POST /api/learning/challenges` cria, `PATCH /api/learning/profile` altera e `DELETE /api/auth/delete-account` apaga. Os dados vão e voltam em JSON.

**3. O que é JSON?**
Um formato de texto para representar objetos: `{"chave": valor}`. No Python, `jsonify(dict)` gera a resposta; no JS, `resposta.json()` lê e `JSON.stringify()` escreve.

**4. Qual a diferença entre Controller, Service, Repository e Model?**
- **Controller:** trata o HTTP.
- **Service:** aplica as regras de negócio.
- **Repository:** acessa o banco.
- **Model:** representa a tabela.

Exemplo: `responder_questao` → `RespostaService.responder` → `RespostaRepository` → `RespostaDesafio`.

**5. Por que a regra de pontuação fica no Service, e não no Controller?**
Porque é regra de negócio. No Service (e em `regras.py`), ela fica num lugar só e pode ser testada sem HTTP. O Controller continua simples: recebe e devolve.

**6. Onde exatamente está a regra de pontuação?**
Os valores e a penalidade estão em `services/aprendizado/regras.py` (`PONTOS_POR_DIFICULDADE`, `penalidade_por_erro`). A aplicação a cada resposta está em `resposta_service.py`. Os bônus de conclusão estão em `conclusao_service.py`.

**7. O que é ORM? Mostre um exemplo do projeto.**
Mapeamento objeto-relacional: as classes Python representam tabelas, e o SQLAlchemy gera o SQL. Exemplo: `RespostaDesafio.query.filter_by(id_aluno=1, id_desafio=7).all()` vira `SELECT * FROM resposta_desafio WHERE id_aluno = 1 AND id_desafio = 7`.

**8. Onde o projeto usa SQL puro e por quê?**
No `AlunoRepository` (`ranking_topo`, `total_participantes`, `participa_do_ranking`, `quantos_a_frente`), com `text()`. A consulta do ranking (filtro, ordenação e desempate) fica explícita e fácil de explicar, e o acesso ao banco permanece na camada Repository.

**9. Como o projeto evita SQL injection?**
Os valores vão como parâmetros (`:limite`, `:pontos`), separados do texto SQL, e o ORM também parametriza tudo. Nenhum valor do usuário é colado dentro do texto da consulta.

**10. O que é uma chave estrangeira? Dê um exemplo.**
É uma coluna que aponta para a chave primária de outra tabela e só aceita valores existentes. Exemplo: `Questao.id_tema = db.ForeignKey("Tema.id_tema")`, ou seja, toda questão pertence a um tema que existe.

**11. Como está implementada a relação entre desafios e questões?**
É uma relação N–N, feita com a tabela de ligação `desafio_questao`, de chave primária composta (`id_desafio`, `id_questao`). O "Refazer" usa isso para reaproveitar as mesmas questões num desafio novo.

**12. Por que a tabela `resposta_desafio` tem uma restrição UNIQUE?**
Para impedir duas respostas do mesmo aluno para a mesma questão do mesmo desafio, mesmo com duplo clique ou duas abas. O banco recusa, e o Service devolve 409 sem somar pontos.

**13. Como funciona a autenticação?**
O login confere o hash da senha (`check_password_hash`) e guarda `aluno_id` na sessão. O decorador `rota()` lê a sessão em cada requisição e responde 401 se não houver aluno.

**14. O que é a sessão e como ela é protegida?**
É um cookie assinado com a `FLASK_SECRET_KEY`. O cookie tem `HttpOnly`, `SameSite=Lax` e, em produção, `Secure`. Chaves fracas ou de exemplo são recusadas, porque permitiriam forjar a sessão.

**15. Como as senhas são guardadas?**
Como hash com sal (`generate_password_hash`, do Werkzeug). Não dá para voltar à senha a partir do hash. Na conferência, o hash é recalculado e comparado.

**16. Como o sistema impede alguém de adivinhar senhas?**
Com o limite de tentativas: 5 erros por e-mail e IP, ou 20 por IP, em 15 minutos, devolvem 429 com `Retry-After`. Além disso, a mensagem e o tempo de resposta são iguais para e-mail inexistente e senha errada.

**17. Por que o painel administrativo está desativado?**
Porque não tem login nem perfis. Ligado, qualquer pessoa poderia alterar pontos, apagar contas e ler o gabarito. O `bloquear_crud_legado` responde 403 a menos que `ENABLE_ADMIN_PANEL=1` (só em desenvolvimento).

**18. O aluno consegue pular para a fase 3 alterando a requisição?**
Não. O `DesafioService.criar` só aceita a fase N se a fase N−1 daquele tema estiver concluída (`fase_concluida`). Senão, grava a fase 1. A dificuldade também é recalculada pelo servidor.

**19. E responder a questão 5 antes da 2?**
Não. O `RespostaService` confere se todas as questões anteriores já têm resposta; se não, devolve 409.

**20. Como funciona a reprovação da jornada?**
Na última fase, o `ConclusaoService` soma as respostas de todas as fases. Se `erradas × 100 ≥ 70 × total`, apaga as fases (e as revisões delas) e retira os pontos que a jornada rendeu. A resposta traz `reprovado: true`.

**21. Como o ranking decide a ordem?**
Mais pontos primeiro; empate pelo nome e depois pelo id. Só entram alunos que já responderam alguma questão. Se o aluno logado não está no topo, a posição dele é calculada contando quantos estão à frente.

**22. Por que a tabela `Ranking` existe se não é usada pelo ranking?**
É legada, do painel administrativo antigo, e foi mantida para não quebrar essas telas. O ranking atual é calculado pelos pontos da tabela `Aluno`.

**23. Como a retomada funciona depois de recarregar a página?**
O desafio, as respostas e os acertos estão no banco. `GET /api/learning/active-challenge` devolve tudo, e o frontend remonta o mapa com ✓ e ✗ e a próxima questão. Como os dados vêm do servidor, a retomada funciona em outro dispositivo também.

**24. Como o frontend chama o backend?**
Pela função `api()` do `estudar.js`, que usa `fetch` com JSON e o cookie de sessão. Na apresentação, dá para mostrar no F12 → Rede.

**25. O que são `async` e `await` no JavaScript?**
`async` marca uma função que faz operações demoradas; `await` espera o resultado de uma (como o `fetch`) sem travar a página. Erros são tratados com `try/catch`.

**26. Como o mapa é desenhado sem SVG?**
`desenharTrilha()` divide cada ligação entre bolinhas numa curva de Bézier e cria várias "pílulas" (`<span>` arredondados) posicionadas e giradas com CSS (`translate` e `rotate`). As bolinhas são `<button>` posicionados por cima da trilha.

**27. Como o projeto evita XSS?**
A área do estudante insere dados com `textContent`, que trata o conteúdo como texto e não como HTML. As páginas do painel antigo passam os dados por `esc()` antes de usar `innerHTML`.

**28. O que acontece se a IA falhar ou não houver chave?**
A IA é chamada até duas vezes. Se não der certo, os temas com banco local usam esse banco, e os outros recebem uma mensagem pedindo para tentar de novo, sem expor o erro técnico. A origem fica registrada em `origem_ia`.

**29. O que os testes automatizados garantem?**
Regras de pontuação, dificuldade e reprovação; segurança (login, bloqueios, posse dos desafios); retomada; aceite dos termos; e o banco local. São 43 testes, rodados com `python -m pytest tests -q`, cada um com um banco temporário.

**30. O que é uma transação e onde aparece no projeto?**
É um conjunto de alterações gravado de uma vez: ou tudo é salvo, ou nada é. `Transacao.confirmar()` faz o commit e `Transacao.desfazer()` faz o rollback. Exemplo: responder grava a resposta, os pontos e o foguinho no mesmo commit.

**31. Como o sistema garante que não ficam dados "órfãos" ao excluir uma conta?**
`services/exclusao.py` apaga primeiro o que aponta para o aluno (respostas, conclusões, ranking legado e desafios) e só depois o aluno. Se algo falhar, o rollback desfaz tudo.

**32. Quais limitações você conhece no projeto?**
- O histórico mostra só os 30 registros mais recentes.
- A pontuação é fixa por dificuldade (não usa a velocidade da resposta, embora o tempo seja registrado).
- As questões são de múltipla escolha comum, sem lacuna.
- O limite de login fica na memória do processo.
- A integração com IA só funciona com uma chave da OpenAI.
