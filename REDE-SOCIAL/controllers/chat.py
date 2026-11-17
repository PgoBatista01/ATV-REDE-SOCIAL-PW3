"""Eventos Socket.IO do chat em tempo real."""

from datetime import datetime

from flask import request, session
from flask_socketio import disconnect, emit


def _autenticado():
    return bool(session.get("usuario_id"))


def _nome_usuario():
    return str(session.get("usuario_nome") or "Cavaleiro")[:80]


def init_app(socketio):
    @socketio.on("connect")
    def handle_connect(auth=None):
        if not _autenticado():
            return False
        print(f"{_nome_usuario()} conectou ao chat. ID: {request.sid}")
        return None

    @socketio.on("disconnect")
    def handle_disconnect(reason=None):
        if _autenticado():
            emit(
                "showmsg",
                {
                    "nickname": _nome_usuario(),
                    "mensagem": f"{_nome_usuario()} saiu do chat.",
                    "tipo": "saida",
                    "horario": datetime.now().strftime("%H:%M"),
                },
                broadcast=True,
            )

    @socketio.on("join")
    def handle_join(data=None):
        if not _autenticado():
            disconnect()
            return
        nome = _nome_usuario()
        emit(
            "showmsg",
            {
                "nickname": nome,
                "mensagem": f"{nome} entrou no Santuário!",
                "tipo": "entrada",
                "horario": datetime.now().strftime("%H:%M"),
            },
            broadcast=True,
        )

    @socketio.on("msg")
    def handle_msg(data):
        if not _autenticado():
            disconnect()
            return
        if not isinstance(data, dict):
            return

        mensagem = data.get("mensagem", data.get("message", ""))
        if not isinstance(mensagem, str):
            return
        mensagem = mensagem.strip()
        if not mensagem or len(mensagem) > 500:
            return

        emit(
            "showmsg",
            {
                "nickname": _nome_usuario(),
                "mensagem": mensagem,
                "horario": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": "mensagem",
            },
            broadcast=True,
        )
