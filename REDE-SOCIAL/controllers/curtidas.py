
from flask import Blueprint, session, redirect, url_for, flash, request
from models.database import db, Post, Curtida


curtidas_bp = Blueprint("curtidas", __name__)


# CURTIR OU DESCURTIR PUBLICAÇÃO
@curtidas_bp.route("/curtir/<int:post_id>", methods=["POST"])
def curtir(post_id):

    # VERIFICAR LOGIN
    if not session.get("user_id"):
        flash("Faça login para interagir com os cavaleiros!", "warning")
        return redirect(url_for("login"))

    usuario_id = session["user_id"]

    # VERIFICAR SE A PUBLICAÇÃO EXISTE
    post = db.session.get(Post, post_id)

    if not post:
        flash("Publicação não encontrada!", "danger")
        return redirect(request.referrer or url_for("galeria"))

    # VERIFICAR SE JÁ CURTIU
    curtida = Curtida.query.filter_by(
        usuario_id=usuario_id,
        post_id=post_id
    ).first()

    if curtida:

        # REMOVER CURTIDA
        db.session.delete(curtida)
        mensagem = "Você removeu sua curtida."

    else:

        # ADICIONAR CURTIDA
        nova_curtida = Curtida(
            usuario_id=usuario_id,
            post_id=post_id
        )

        db.session.add(nova_curtida)
        mensagem = "Você curtiu esta publicação!"

    try:
        db.session.commit()
        flash(mensagem, "success")

    except Exception:
        db.session.rollback()
        flash("Não foi possível registrar sua curtida.", "danger")

    return redirect(request.referrer or url_for("galeria"))


# CONSULTAR QUANTIDADE DE CURTIDAS
@curtidas_bp.route("/curtidas/<int:post_id>")
def quantidade_curtidas(post_id):

    total = Curtida.query.filter_by(
        post_id=post_id
    ).count()

    return {"post_id": post_id, "total_curtidas": total}
