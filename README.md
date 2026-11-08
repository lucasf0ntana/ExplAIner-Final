# ExplAIner 

**ExplAIner** é uma plataforma de estudos gamificada que utiliza Inteligência Artificial para gerar questões de múltipla escolha com base no tema escolhido pelo usuário. O sistema permite selecionar a dificuldade, quantidade de fases e acompanhar a pontuação, ranking e sequência de acertos (foguinho/streak), tornando o estudo mais dinâmico, rápido e eficiente para alunos do Ensino Médio.

## Integrantes da Equipe
* Lucas Ribeiro Fontana
* Josué Fernando Silva Melo
* Weber Anjos de Souza Sodré
* Álvaro Pires de Souza
* Antônio Henrique de Paula Reis
* Henrique Saddi Meinicke

## Stack Tecnológica
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla ES6+)
* **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-CORS
* **Banco de Dados:** MySQL

---

## Visão geral

Projeto de API Flask com frontend estático para um sistema de gamificação educacional.
O backend serve o frontend diretamente a partir da pasta `frontend/` e expõe rotas CRUD para as principais models.

## Models implementadas

- `Aluno`
- `Tema`
- `Desafio`
- `Questao`
- `Ranking`
- `AlunoDesafio` (suporte backend)
- `DesafioQuestao` (suporte backend)

## Rotas principais implementadas

- `/` - página inicial do frontend
- `/api` - documentação simples da API

### Aluno
- `GET /alunos`
- `GET /alunos/<id>`
- `POST /alunos`
- `PUT /alunos/<id>`
- `DELETE /alunos/<id>`

### Tema
- `GET /temas`
- `POST /temas`
- `PUT /temas/<id_tema>`
- `DELETE /temas/<id_tema>`

### Desafio
- `GET /desafio`
- `GET /desafio/nome/<nome>`
- `POST /desafio`
- `PUT /desafio/<id_desafio>`
- `DELETE /desafio/<id_desafio>`

### Questao
- `GET /questoes`
- `POST /questoes`
- `PUT /questoes/<id_questao>`
- `DELETE /questoes/<id_questao>`

### Ranking
- `GET /ranking`
- `POST /ranking`
- `PUT /ranking/<id_ranking>`
- `DELETE /ranking/<id_ranking>`

### Relacionamentos adicionais (backend)
- `POST /alunos/desafios`
- `GET /alunos/<id_aluno>/desafios`
- `PUT /alunos/<id_aluno>/desafios/<id_desafio>`
- `POST /desafios/<id_desafio>/questoes/<id_questao>`
- `GET /desafios/<id_desafio>/questoes`
- `DELETE /desafios/<id_desafio>/questoes/<id_questao>`

## Telas/front-end implementadas

- `index.html` - cadastro de aluno
- `ler.html` - buscar aluno por ID
- `listar.html` - listar alunos
- `atualizar.html` - atualizar aluno
- `deletar.html` - excluir aluno
- `temas.html` - cadastrar e listar temas
- `desafios.html` - cadastrar e listar desafios
- `questoes.html` - cadastrar e listar questões
- `ranking.html` - cadastrar e listar ranking

## Observações

- O backend serve os arquivos estáticos do frontend. Para rodar o projeto, basta iniciar o backend.
- As rotas CRUD do backend existem para todas as models principais.
- No frontend, as funcionalidades de criar, listar, atualizar e excluir estão disponíveis para `Aluno`, `Tema`, `Desafio`, `Questao` e `Ranking`.
- O backend também possui endpoints adicionais para os relacionamentos `AlunoDesafio` e `DesafioQuestao`, embora não existam telas específicas para esses relacionamentos no frontend.

---

## Como Executar o Projeto

Antes de começar, certifique-se de ter instalado em sua máquina:
* **Python 3.x**
* **Git** (opcional)

---

## 💻 Passo a Passo para Rodar o Projeto

Siga os comandos abaixo no seu terminal (Prompt de Comando ou PowerShell):

### 1. Acessar a pasta do backend
```bash
cd backend
```

### 2. Criar o Ambiente Virtual (.venv)
Cria um ambiente isolado para evitar conflitos de bibliotecas globais:
```bash
python -m venv .venv
```

### 3. Ativar o Ambiente Virtual
* **No Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\activate
  ```
* **No Windows (Prompt de Comando - CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
### 4. Mude o arquivo "env.example.txt" para ".env.example"

### 5. Configurar as Variáveis de Ambiente
Crie o arquivo `.env` copiando as configurações de exemplo:
```bash
cp .env.example .env
```
*(Se o comando `cp` não funcionar no CMD do Windows, use: `copy .env.example .env`)*

### 6. Instalar as Dependências
Para evitar erros de scripts corrompidos (`Fatal error in launcher`), instale as dependências chamando diretamente o executável do Python do ambiente:

```powershell
# Instalar pacotes do arquivo de requerimentos
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Garantir a instalação dos pacotes principais e drivers de banco
.\.venv\Scripts\python.exe -m pip install flask flask-sqlalchemy pymysql
```

### 7. Executar a Aplicação
Inicie o servidor Flask utilizando o Python do ambiente virtual:
```bash
.\.venv\Scripts\python.exe app.py
```

A API ficará disponível em:

```text
http://127.0.0.1:5000
```
---

## Banco de dados

Por padrão, o projeto usa SQLite para facilitar o teste local:

```text
DATABASE_URL=sqlite:///explainer.db
```

Para usar MySQL, execute o script:

```text
backend/database/create_database.sql
```

Depois altere o `.env` para:

```text
DATABASE_URL=mysql+pymysql://root:sua_senha@localhost:3306/explainer
```

## 🐛 Resolução de Problemas Comuns

### Erro: "Fatal error in launcher: Unable to create process..."
Esse erro ocorre no Windows quando a pasta do projeto é movida de lugar ou sincronizada no OneDrive. 
* **Solução:** Nunca use o comando `pip install` diretamente se o erro persistir. Use sempre o prefixo `.\.venv\Scripts\python.exe -m pip install <pacote>`.


## Como executar o frontend

Em outro terminal, entre na pasta do frontend:

```bash
cd frontend
```

Execute um servidor local:

```bash
python -m http.server 5500
```

Acesse:

```text
http://127.0.0.1:5500
```
## Funcionalidades Implementadas

1. O sistema deve pedir a senha e o email do usuário para fazer o cadastro.
2. O sistema deve pedir qual o nome de usuário para salvar no banco de dados.
3. O sistema deve permitir ao usuário escolher qual tema estudar.
4. O sistema deve sugerir de qual matéria o tema escolhido faz parte.
5. O sistema deve oferecer uma escolha do nível de dificuldade dos desafios para
o usuário escolher.
6. O sistema deve oferecer uma escolha da quantidade de desafios
que vão ser feitos
7. O sistema deve fazer os desafios em forma de fases como o duolingo e alguns
jogos.
8. O sistema deve mostrar a quantidade de pontos do usuário com base no desempenho dele em cada fase.
9. O sistema deve mostrar um ranking de usuários.
10. O sistema deve mostrar a posição e os pontos de cada usuário.
11. O sistema deve deixar o usuário olhar todas as atividades anteriores.
12. O sistema deve deixar o usuário refazer as atividades feitas anteriormente.
13. O sistema deve mostrar para o usuário, quando ele acabar uma questao,
deverá mudar o fundo da alternativa marcada para vermelho, para mostrar que ele errou.
14. O sistema deve mostrar para o usuário, quando ele acabaruma questao,
deverá mudar o fundo da alternativa marcada para verde, para mostrar que ele acertou.
15. O sistema deve fazer um esquema de pontos por vitória igual no kahoot.
16. O sistema deve permitir que o usuário continue um desafio de onde parou, salvando automaticamente seu progresso.
17. O sistema deve criar um sistema para incentivar o usuário a usar o aplicativo
todo dia, como o sistema de foguinho no duolingo.
18. O sistema deve fazer as questoes em múltipla escolha.
19. O sistema deve registrar automaticamente todo o progresso em um único
painel.
20. O sistema deve mandar elogios e comemorações para usuário, a cada desafio que você conclui.
