
import os
import pymysql
import pymysql.cursors

from flask import Flask
from flask_socketio import SocketIO

from models.database import db
from controllers import routes, chat
from controllers.desafios import desafios_bp


# NOME DO BANCO DE DADOS
DB_NAME = 'cdz'


# CONFIGURACAO DO FLASK
app = Flask(__name__, template_folder='views')

app.config['DATABASE_NAME'] = DB_NAME

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://root:@localhost/{DB_NAME}'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'meusegredo'

app.config['PERMANENT_SESSION_LIFETIME'] = 3600

app.config['UPLOAD_FOLDER'] = os.path.join(
    app.static_folder, 'uploads'
)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# CRIAR PASTA DE UPLOADS
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# INICIALIZACAO DO SQLALCHEMY
db.init_app(app)


# CONFIGURACAO DO SOCKET.IO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)


# REGISTRO DAS ROTAS
routes.init_app(app)
app.register_blueprint(desafios_bp)

# REGISTRO DOS EVENTOS DO CHAT
chat.init_app(socketio)


if __name__ == '__main__':

    # CONEXAO COM O MYSQL
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                f'CREATE DATABASE IF NOT EXISTS `{DB_NAME}`'
            )

        print('Banco de dados CDZ criado ou já existente!')

    except Exception as error:

        print(f'Erro ao criar o banco: {error}')

    finally:

        connection.close()


    # CRIACAO DAS TABELAS
    with app.app_context():

        db.create_all()

        print('Tabelas do CDZ criadas ou já existentes!')


    # INICIALIZACAO DO SERVIDOR
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )
