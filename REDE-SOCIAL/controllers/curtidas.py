"""Curtidas temporárias para Cavaleiros, mantidas na sessão do navegador.

O projeto não possui modelos Post/Curtida; por isso as curtidas não são
partilhadas nem persistidas na base de dados.
"""

from flask import Blueprint, abort, flash, jsonify, redirect, request, session, url_for

from models.database import Cavaleiro

curtidas_bp = Blueprint("curtidas", __name__)


@curtidas_bp.post("/curtir/<int:post_id>")
def curtir(post_id):
    if not session.get("usuario_id"):
        flash("Faça login para interagir com os Cavaleiros!", "warning")
        return redirect(url_for("login", next=request.referrer or url_for("feed")))

    cavaleiro = Cavaleiro.query.get_or_404(post_id)
    curtidas = session.get("curtidas_cavaleiros", [])
    if not isinstance(curtidas, list):
        curtidas = []

    id_texto = str(cavaleiro.id)
    if id_texto in curtidas:
        curtidas.remove(id_texto)
        flash("Você removeu sua curtida.", "info")
    else:
        curtidas.append(id_texto)
        flash("Você curtiu esta publicação!", "success")

    session["curtidas_cavaleiros"] = curtidas
    return redirect(request.referrer or url_for("feed"))


@curtidas_bp.get("/curtidas/<int:post_id>")
def quantidade_curtidas(post_id):
    cavaleiro = Cavaleiro.query.get_or_404(post_id)
    curtidas = session.get("curtidas_cavaleiros", [])
    return jsonify({
        "post_id": cavaleiro.id,
        "total_curtidas": int(str(cavaleiro.id) in curtidas),
        "curtido": str(cavaleiro.id) in curtidas,
    })
