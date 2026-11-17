"""Rotas auxiliares para visualizar o perfil público de outro usuário."""

from flask import Blueprint, abort, render_template

from models.database import Usuario, db

perfil_bp = Blueprint("perfil", __name__)


@perfil_bp.route("/perfil/<int:usuario_id>")
def visualizar_perfil(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario is None:
        abort(404)
    return render_template("perfil.html", usuario=usuario, visualizar=True)
