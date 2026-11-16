
from flask import request, session
from flask_socketio import emit, disconnect
from datetime import datetime


def init_app(socketio):

    # USUARIO SE CONECTOU
    @socketio.on("connect")
    def handle_connect():

        if not session.get("user_id"):
            print("Conexao recusada: usuario nao autenticado.")
            return False

        nome = session.get("usuario_nome", "Cavaleiro")

        print(f"{nome} se conectou. ID: {request.sid}")

    # USUARIO SE DESCONECTOU
    @socketio.on("disconnect")
    def handle_disconnect():

        nome = session.get("usuario_nome", "Cavaleiro")

        print(f"{nome} se desconectou. ID: {request.sid}")

        emit("join", {
            "nickname": nome,
            "mensagem": f"{nome} saiu do chat.",
            "tipo": "saida"
        }, broadcast=True)

    # USUARIO ENTROU NO CHAT
    @socketio.on("join")
    def handle_join(data=None):

        if not session.get("user_id"):
            disconnect()
            return

        nome = session.get("usuario_nome", "Cavaleiro")

        print(f"{nome} entrou no chat.")

        emit("join", {
            "nickname": nome,
            "mensagem": f"{nome} entrou no Santuário!",
            "tipo": "entrada"
        }, broadcast=True)

    # ENVIO DE MENSAGENS
    @socketio.on("msg")
    def handle_msg(data):

        if not session.get("user_id"):
            disconnect()
            return

        if not isinstance(data, dict):
            return

        nome = session.get("usuario_nome", "Cavaleiro")

        mensagem = data.get("mensagem", data.get("message", ""))

        if not isinstance(mensagem, str):
            return

        mensagem = mensagem.strip()

        if not mensagem:
            return

        if len(mensagem) > 500:
            return

        horario = datetime.now().strftime("%d/%m/%Y %H:%M")

        dados_mensagem = {
            "nickname": nome,
            "mensagem": mensagem,
            "horario": horario,
            "tipo": "mensagem"
        }

        print(f"[{horario}] {nome}: {mensagem}")

        emit("showmsg", dados_mensagem, broadcast=True)
