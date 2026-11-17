# Santuário Social — Cavaleiros do Zodíaco

## Requisitos

- Python 3.10 ou superior
- MySQL em execução (a aplicação cria a base `santuario_social` se o utilizador tiver permissão)

## Instalação

Na pasta do projeto, crie e ative um ambiente virtual e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuração

A aplicação aceita estas variáveis de ambiente:

- `DB_HOST` (predefinição: `localhost`)
- `DB_USER` (predefinição: `root`)
- `DB_PASSWORD` (predefinição: vazia)
- `DB_NAME` (predefinição: `santuario_social`; se estiver definido, `DATABASE_URL` prevalece)
- `DATABASE_URL` (opcional; substitui a ligação MySQL)
- `SECRET_KEY` (defina um valor aleatório, sobretudo fora do ambiente local)
- `HOST`, `PORT` e `FLASK_DEBUG` (opcionais)

Exemplo no PowerShell:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "a-sua-senha-mysql"
$env:SECRET_KEY = "substitua-por-uma-chave-aleatoria-longa"
```

## Execução

```powershell
python app.py
```

Abra `http://localhost:5000`. Na primeira execução, `app.py` cria a base de dados e as tabelas a partir de `models/database.py`, e acrescenta os Cavaleiros e publicações iniciais que ainda não existam. A carga é idempotente: não apaga nem substitui registos existentes. Se o projeto tiver sido configurado com `DATABASE_URL`, confirme que essa URL aponta para `santuario_social` ou remova-a para usar `DB_NAME`.

## Notas funcionais

- O login e as rotas autenticadas usam `session["usuario_id"]`.
- Os campos de perfil correspondem ao modelo existente: `personagem_favorito` e `carta_favorita`.
- O quiz está disponível em `/desafios`; cada resposta certa soma 10 pontos ao utilizador autenticado.
- A galeria guarda imagens em `static/uploads` e permite que cada utilizador apague apenas as próprias publicações.
- O feed mostra as publicações dos Cavaleiros (`PublicacaoCavaleiro`) e as imagens partilhadas pelos utilizadores (`Imagem`).
- As curtidas são apenas temporárias na sessão; o projeto não possui tabelas `Post` ou `Curtida`.
