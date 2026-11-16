
import os
import uuid

from flask import (
    Blueprint, render_template, request,
    session, redirect, url_for, flash, current_app
)

from werkzeug.utils import secure_filename
from models.database import db, Usuario


perfil_bp = Blueprint("perfil", __name__)

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "gif"}


# VERIFICAR EXTENSAO DA IMAGEM
def imagem_permitida(nome):

    return (
        "." in nome
        and nome.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )


# PAGINA DO PERFIL
@perfil_bp.route("/perfil", methods=["GET", "POST"])
def perfil():

    if not session.get("user_id"):
        flash("Entre no Santuário para acessar seu perfil!", "warning")
        return redirect(url_for("login"))

    usuario = db.session.get(Usuario, session["user_id"])

    if not usuario:
        session.clear()
        flash("Usuário não encontrado. Faça login novamente.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        # ATUALIZAR INFORMACOES
        campos = {
            "nome": request.form.get("nome", "").strip(),
            "biografia": request.form.get("biografia", "").strip(),
            "signo": request.form.get("signo", "").strip(),
            "cavaleiro_favorito": request.form.get(
                "cavaleiro_favorito", ""
            ).strip(),
            "armadura_favorita": request.form.get(
                "armadura_favorita", ""
            ).strip()
        }

        if not campos["nome"]:
            flash("O nome do cavaleiro não pode ficar vazio!", "warning")
            return redirect(url_for("perfil.perfil"))

        for campo, valor in campos.items():
            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)

        # ATUALIZAR FOTO DE PERFIL
        arquivo = request.files.get("foto_perfil")

        if arquivo and arquivo.filename:

            if not imagem_permitida(arquivo.filename):
                flash("Formato de imagem não permitido!", "danger")
                return redirect(url_for("perfil.perfil"))

            extensao = secure_filename(
                arquivo.filename
            ).rsplit(".", 1)[1].lower()

            nome_arquivo = f"{uuid.uuid4().hex}.{extensao}"

            pasta = current_app.config["UPLOAD_FOLDER"]

            os.makedirs(pasta, exist_ok=True)

            caminho = os.path.join(pasta, nome_arquivo)

            arquivo.save(caminho)

            if hasattr(usuario, "foto_perfil"):
                usuario.foto_perfil = nome_arquivo

        try:
            db.session.commit()

            session["usuario_nome"] = getattr(
                usuario, "nome", session.get("usuario_nome")
            )

            flash("Seu perfil foi atualizado com sucesso!", "success")

        except Exception:
            db.session.rollback()
            flash("Não foi possível atualizar seu perfil.", "danger")

        return redirect(url_for("perfil.perfil"))

    return render_template(
        "perfil.html",
        usuario=usuario
    )


# VISUALIZAR PERFIL DE OUTRO CAVALEIRO
@perfil_bp.route("/perfil/<int:usuario_id>")
def visualizar_perfil(usuario_id):

    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        flash("Cavaleiro não encontrado!", "warning")
        return redirect(url_for("index"))

    return render_template(
        "perfil.html",
        usuario=usuario,
        visualizar=True
    )
