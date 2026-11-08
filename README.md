# ExplAIner

**ExplAIner** é uma plataforma de estudos gamificada que usa Inteligência Artificial para gerar questões de múltipla escolha sobre o tema escolhido pelo aluno. O aluno define a dificuldade e o tamanho das fases e acompanha pontuação, ranking e sequência de dias de estudo (foguinho), tornando o estudo mais dinâmico, rápido e eficiente para alunos do Ensino Médio.

**Site hospedado:** https://COLOQUE-AQUI-O-LINK.onrender.com

## Integrantes da Equipe
* Lucas Ribeiro Fontana
* Josué Fernando Silva Melo
* Weber Anjos de Souza Sodré
* Álvaro Pires de Souza
* Antônio Henrique de Paula Reis
* Henrique Saddi Meinicke

## Stack Tecnológica
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla ES6+)
* **Backend:** Python, Flask, Flask-SQLAlchemy (ORM), Flask-CORS
* **Inteligência Artificial:** API da OpenAI (geração das questões)
* **Banco de Dados:** SQLite (local), PostgreSQL (hospedado) e MySQL (opcional, com `create_database.sql`)
* **Hospedagem:** Render (`render.yaml`) com Gunicorn
* **Testes:** pytest

---

## Visão geral

O frontend (`frontend/`) e a API (`backend/`) ficam separados. O frontend consome a API por requisições `fetch` em JSON, e o Flask também entrega os arquivos do frontend, então basta iniciar o backend.

O backend segue a arquitetura em camadas:

| Camada | Pasta | Responsabilidade |
|---|---|---|
| Controller | `backend/controllers/` | Recebe a requisição HTTP, confere o login e devolve o JSON |
| Service | `backend/services/` | Executa o caso de uso e as regras da aplicação |
| Repository | `backend/repositories/` | Acessa o banco (ORM e consultas SQL do ranking) |
| Model | `backend/models/` | Representa as tabelas |

## Models implementadas

- `Aluno`
- `Tema`
- `Desafio`
- `Questao`
- `RespostaDesafio`
- `AlunoDesafio`
- `DesafioQuestao`
- `Ranking` (painel administrativo legado)

## Rotas principais

- `/` - área do estudante (`estudar.html`)
- `/api` - documentação simples da API

### Conta
- `POST /api/auth/register` - cadastro (exige aceite dos termos)
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/accept-terms` - registra o aceite dos termos
- `DELETE /api/auth/delete-account`

### Aprendizado
- `GET /api/learning/me` - dados e progresso do aluno
- `PATCH /api/learning/profile` - alterar o nick
- `GET /api/learning/catalog` - matérias e temas
- `GET /api/learning/active-challenge` - desafio em andamento
- `POST /api/learning/challenges` - gerar desafio com IA (ou refazer um antigo)
- `GET /api/learning/challenges/<id>`
- `POST /api/learning/challenges/<id>/answer` - responder questão
- `POST /api/learning/challenges/<id>/complete` - concluir fase
- `POST /api/learning/activity` - tempo ativo
- `GET /api/learning/ranking`
- `GET /api/learning/history`

### Painel administrativo legado (CRUD)
Desligado por padrão. Para usar no computador, defina `ENABLE_ADMIN_PANEL=1` no `.env` (nunca em produção, porque o painel não tem login).

- Aluno: `GET/POST /alunos`, `GET/PUT/DELETE /alunos/<id>`, `GET /alunos/ranking`
- Tema: `GET/POST /temas`, `PUT/DELETE /temas/<id_tema>`
- Desafio: `GET/POST /desafio`, `GET /desafio/nome/<nome>`, `PUT/DELETE /desafio/<id_desafio>`
- Questão: `GET/POST /questoes`, `PUT/DELETE /questoes/<id_questao>`, `POST /questoes/<id_questao>/verificar`
- Ranking: `GET/POST /ranking`, `PUT/DELETE /ranking/<id_ranking>`
- Relacionamentos: `POST /alunos/desafios`, `GET /alunos/<id_aluno>/desafios`, `PUT /alunos/<id_aluno>/desafios/<id_desafio>`, `POST/DELETE /desafios/<id_desafio>/questoes/<id_questao>`, `GET /desafios/<id_desafio>/questoes`

## Telas

- `estudar.html` - área do estudante: login, cadastro, aprender, mapa de questões, ranking e progresso
- `termos-de-uso.html` e `termo-de-consentimento.html` - termos aceitos no cadastro
- `index.html`, `ler.html`, `listar.html`, `atualizar.html`, `deletar.html`, `temas.html`, `desafios.html`, `questoes.html` e `ranking.html` - painel administrativo legado (CRUD)

---

## Como executar o projeto

Antes de começar, instale:
* **Python 3.12 ou mais novo**
* **Git** (opcional)

Rode os comandos no terminal (PowerShell), **na pasta raiz do projeto**:

### 1. Criar o ambiente virtual
```powershell
python -m venv .venv
```

### 2. Ativar o ambiente virtual
* **PowerShell:**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
* **Prompt de Comando (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

### 3. Instalar as dependências
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente
Crie o arquivo `.env` na raiz do projeto a partir do exemplo:
```powershell
copy .env.example .env
```

Depois, edite o `.env`:
* `FLASK_SECRET_KEY`: gere uma chave com `python -c "import secrets; print(secrets.token_hex(32))"` e cole o resultado.
* `OPENAI_API_KEY`: a chave da OpenAI que gera as questões.

O `.env` está no `.gitignore` e **nunca** deve ser enviado ao GitHub.

### 5. Executar a aplicação
```powershell
.\.venv\Scripts\python.exe backend\app.py
```

Acesse:

```text
http://127.0.0.1:5000
```

### 6. Rodar os testes (opcional)
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

---

## Banco de dados

Por padrão, o projeto usa SQLite para facilitar o teste local (arquivo `instance/explainer.db`, na raiz do projeto). As tabelas são criadas sozinhas na primeira execução.

Para usar outro banco, defina `DATABASE_URL` no `.env`:

* **PostgreSQL** (usado na hospedagem, por exemplo com o Neon):
  ```text
  DATABASE_URL=postgresql://usuario:senha@servidor/banco
  ```
* **MySQL:** execute `backend/database/create_database.sql` e use:
  ```text
  DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/ExplAIner
  ```

## Hospedagem

O projeto está pronto para o Render pelo arquivo `render.yaml`. No Render, crie um **Blueprint** a partir deste repositório e informe `OPENAI_API_KEY` e `DATABASE_URL`. A cada `git push` na branch `main`, o site é atualizado sozinho.

---

## Resolução de problemas comuns

### Erro: "Fatal error in launcher: Unable to create process..."
Acontece no Windows quando a pasta do projeto é movida ou sincronizada no OneDrive.
* **Solução:** use sempre `.\.venv\Scripts\python.exe -m pip install <pacote>` em vez de `pip install`.

### O PowerShell não deixa ativar o ambiente virtual
Rode uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## Funcionalidades implementadas

1. Cadastro com e-mail e senha (a senha é guardada com hash).
2. Nome de usuário (nick) salvo no banco de dados e editável no perfil.
3. Escolha do tema a estudar.
4. Organização dos temas por matéria: o aluno escolhe a matéria e vê os temas dela.
5. Escolha do nível de dificuldade inicial (Fácil, Médio ou Difícil).
6. Escolha da quantidade de questões por fase (5, 10, 15 ou 20), que define quantas fases a jornada tem.
7. Desafios em forma de fases, com um mapa de questões, como no Duolingo.
8. Pontuação do aluno com base no desempenho em cada fase, com bônus por fase perfeita e por jornada concluída.
9. Ranking de usuários.
10. Posição e pontos de cada usuário no ranking, inclusive a posição de quem está fora do topo.
11. Histórico das atividades anteriores (as 30 mais recentes).
12. Refazer atividades já concluídas (modo revisão, sem pontos).
13. Alternativa marcada em vermelho quando o aluno erra a questão.
14. Alternativa marcada em verde quando o aluno acerta a questão.
15. Pontos por acerto que variam com a dificuldade, inspirado no Kahoot.
16. Continuar um desafio de onde parou, com o progresso salvo automaticamente.
17. Sequência de dias de estudo (foguinho) para incentivar o uso diário, como no Duolingo.
18. Questões de múltipla escolha geradas por Inteligência Artificial.
19. Painel "Meu progresso" com todo o progresso do aluno.
20. Elogios e comemorações a cada desafio concluído.
21. Termos de Uso e Termo de Consentimento, com a data e a versão do aceite registradas.
22. Exclusão da própria conta, apagando todos os dados do aluno.
