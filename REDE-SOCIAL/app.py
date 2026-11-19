"""Ponto de entrada da aplicação Santuário Social."""

import os
from urllib.parse import quote_plus

import pymysql
import pymysql.cursors
from flask import Flask
from flask_socketio import SocketIO

from models.database import Cavaleiro, PublicacaoCavaleiro, db
from controllers import chat, routes
from controllers.personagens_ia import personagens_ia_bp
from controllers.desafios import desafios_bp
from controllers.perfil import perfil_bp
from controllers.curtidas import curtidas_bp


DB_NAME = os.environ.get("DB_NAME", "santuario_social")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
MYSQL_URI = (
    f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}/{quote_plus(DB_NAME)}?charset=utf8mb4"
)

app = Flask(__name__, template_folder="views")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", MYSQL_URI)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-this-secret")
app.config["PERMANENT_SESSION_LIFETIME"] = 3600
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder or "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

routes.init_app(app)
app.register_blueprint(desafios_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(curtidas_bp)
app.register_blueprint(personagens_ia_bp)
chat.init_app(socketio)


# Dados demonstrativos acrescentados apenas quando ainda não existem.
# As imagens abaixo já estão em static/imgs; não se substituem dados do utilizador.
CAVALEIROS_INICIAIS = [
    ("Seiya de Pégaso", "Pégaso", "Bronze", "Armadura de Pégaso", "Meteoro de Pégaso", "Determinado e corajoso, Seiya protege Atena e nunca desiste dos seus companheiros.", "seiya.png"),
    ("Shiryu de Dragão", "Dragão", "Bronze", "Armadura de Dragão", "Cólera do Dragão", "Sábio e disciplinado, Shiryu luta com honra e grande espírito de justiça.", "shiryu.png"),
    ("Hyoga de Cisne", "Cisne", "Bronze", "Armadura de Cisne", "Pó de Diamante", "Hyoga domina técnicas de gelo e combate com serenidade e precisão.", "hyoga.png"),
    ("Shun de Andrômeda", "Andrômeda", "Bronze", "Armadura de Andrômeda", "Corrente de Andrômeda", "Gentil e compassivo, Shun prefere evitar o combate, mas defende os amigos com coragem.", "shun.png"),
    ("Ikki de Fênix", "Fênix", "Bronze", "Armadura de Fênix", "Ave Fênix", "De personalidade forte, Ikki é conhecido pela resistência e pelo poder da Fênix.", "ikki.png"),
    ("Mu de Áries", "Áries", "Ouro", "Armadura de Ouro de Áries", "Reparação de Armaduras", "Guardião da primeira Casa, Mu é mestre na reparação de armaduras.", "mu.png"),
    ("Aldebaran de Touro", "Touro", "Ouro", "Armadura de Ouro de Touro", "Grande Chifre", "Guardião da segunda Casa, é reconhecido pela força e pela lealdade.", "aldebaran.png"),
    ("Saga de Gêmeos", "Gêmeos", "Ouro", "Armadura de Ouro de Gêmeos", "Explosão Galáctica", "Guardião da terceira Casa, possui um poder imenso e uma história complexa.", "saga.png"),
    ("Máscara da Morte de Câncer", "Câncer", "Ouro", "Armadura de Ouro de Câncer", "Ondas do Inferno", "Guardião da quarta Casa, domina técnicas ligadas ao mundo dos mortos.", "mascara-da-morte.png"),
    ("Aiolia de Leão", "Leão", "Ouro", "Armadura de Ouro de Leão", "Relâmpago de Plasma", "Guardião da quinta Casa, luta com velocidade, coragem e lealdade.", "aiolia.png"),
    ("Shaka de Virgem", "Virgem", "Ouro", "Armadura de Ouro de Virgem", "Tesouro do Céu", "Guardião da sexta Casa, é conhecido como o homem mais próximo de Deus.", "shaka.png"),
    ("Dohko de Libra", "Libra", "Ouro", "Armadura de Ouro de Libra", "Cólera dos Cem Dragões", "Guardião da sétima Casa, é um mestre sábio e experiente.", "dohko.png"),
    ("Milo de Escorpião", "Escorpião", "Ouro", "Armadura de Ouro de Escorpião", "Agulha Escarlate", "Guardião da oitava Casa, ataca com precisão através da Agulha Escarlate.", "milo.png"),
    ("Aiolos de Sagitário", "Sagitário", "Ouro", "Armadura de Ouro de Sagitário", "Flecha de Sagitário", "Guardião da nona Casa, é lembrado pela coragem e pela lealdade a Atena.", "aiolos.png"),
    ("Shura de Capricórnio", "Capricórnio", "Ouro", "Armadura de Ouro de Capricórnio", "Excalibur", "Guardião da décima Casa, domina a técnica de espada Excalibur.", "shura.png"),
    ("Camus de Aquário", "Aquário", "Ouro", "Armadura de Ouro de Aquário", "Execução Aurora", "Guardião da décima primeira Casa, é mestre das técnicas de gelo.", "camus.png"),
    ("Afrodite de Peixes", "Peixes", "Ouro", "Armadura de Ouro de Peixes", "Rosas Diabólicas Reais", "Guardião da décima segunda Casa, combate com rosas de diferentes poderes.", "afrodite.png"),
]


def popular_dados_iniciais():
    """Acrescenta personagens e uma publicação-semente por personagem, sem sobrescrever dados."""
    for nome, constelacao, categoria, armadura, poder, descricao, filename in CAVALEIROS_INICIAIS:
        cavaleiro = Cavaleiro.query.filter_by(nome=nome).first()
        if cavaleiro is None:
            cavaleiro = Cavaleiro(
                nome=nome,
                constelacao=constelacao,
                categoria=categoria,
                armadura=armadura,
                poder=poder,
                descricao=descricao,
                imagem=f"imgs/{filename}",
            )
            db.session.add(cavaleiro)
            db.session.flush()

        legenda = f"Conheça {nome}. {descricao}"
        publicacao_existente = PublicacaoCavaleiro.query.filter_by(
            cavaleiro_id=cavaleiro.id,
            legenda=legenda,
        ).first()
        if publicacao_existente is None:
            db.session.add(
                PublicacaoCavaleiro(
                    cavaleiro_id=cavaleiro.id,
                    legenda=legenda,
                    imagem=f"imgs/{filename}",
                )
            )

    db.session.commit()


def preparar_banco():
    """Cria a base/tabelas necessárias e acrescenta dados iniciais idempotentes."""
    if (
        not os.environ.get("DATABASE_URL")
        and app.config["SQLALCHEMY_DATABASE_URI"].startswith("mysql")
    ):
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
        finally:
            connection.close()

    with app.app_context():
        db.create_all()
        popular_dados_iniciais()


if __name__ == "__main__":
    preparar_banco()
    socketio.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
