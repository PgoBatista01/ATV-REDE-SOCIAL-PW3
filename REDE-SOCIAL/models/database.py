
from flask_sqlalchemy import SQLAlchemy

# INICIALIZANDO O SQLALCHEMY
db = SQLAlchemy()


# TABELA DE CAVALEIROS
class Cavaleiro(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    constelacao = db.Column(db.String(100))
    categoria = db.Column(db.String(100))
    armadura = db.Column(db.String(150))
    poder = db.Column(db.String(150))
    descricao = db.Column(db.Text)
    imagem = db.Column(db.String(255))

    def __init__(self, nome, constelacao, categoria, armadura,
                 poder, descricao, imagem=None):

        self.nome = nome
        self.constelacao = constelacao
        self.categoria = categoria
        self.armadura = armadura
        self.poder = poder
        self.descricao = descricao
        self.imagem = imagem


# TABELA DE CURIOSIDADES
class Curiosidade(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)

    def __init__(self, titulo, descricao):

        self.titulo = titulo
        self.descricao = descricao


# TABELA DE USUARIOS
class Usuario(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    biografia = db.Column(db.Text)
    personagem_favorito = db.Column(db.String(100))
    carta_favorita = db.Column(db.String(100))
    foto_perfil = db.Column(db.String(255))

    pontos = db.Column(db.Integer, default=0)

    def __init__(self, nome, nickname, email, senha):

        self.nome = nome
        self.nickname = nickname
        self.email = email
        self.senha = senha


# TABELA DE IMAGENS
class Imagem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    legenda = db.Column(db.Text)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    usuario = db.relationship(
        'Usuario',
        backref=db.backref('imagens', lazy=True)
    )

    def __init__(self, filename, legenda=None, usuario_id=None):

        self.filename = filename
        self.legenda = legenda
        self.usuario_id = usuario_id
