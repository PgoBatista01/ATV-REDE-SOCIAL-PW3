"""Desafios de conhecimentos com pontuação persistida no perfil."""

import secrets

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.database import Usuario, db


desafios_bp = Blueprint("desafios", __name__)

PERGUNTAS = [
    {
        "id": 1,
        "pergunta": "Qual é o cavaleiro de bronze conhecido pela Armadura de Pégaso?",
        "opcoes": ["Shiryu", "Seiya", "Hyoga", "Shun"],
        "resposta": "Seiya",
    },
    {
        "id": 2,
        "pergunta": "Qual é o nome da deusa que os cavaleiros protegem?",
        "opcoes": ["Ártemis", "Afrodite", "Atena", "Hera"],
        "resposta": "Atena",
    },
    {
        "id": 3,
        "pergunta": "Qual cavaleiro utiliza a Armadura de Dragão?",
        "opcoes": ["Ikki", "Shiryu", "Seiya", "Hyoga"],
        "resposta": "Shiryu",
    },
    {
        "id": 4,
        "pergunta": "Qual é o cavaleiro de bronze associado ao Cisne?",
        "opcoes": ["Shun", "Hyoga", "Ikki", "Shiryu"],
        "resposta": "Hyoga",
    },
    {
        "id": 5,
        "pergunta": "Qual é o nome do cavaleiro de Fênix?",
        "opcoes": ["Ikki", "Seiya", "Shun", "Hyoga"],
        "resposta": "Ikki",
    },
    {
        "id": 6,
        "pergunta": "Quantas são as Casas do Zodíaco no Santuário?",
        "opcoes": ["7", "10", "12", "15"],
        "resposta": "12",
    },
    {
        "id": 7,
        "pergunta": "Qual é a armadura de Shun?",
        "opcoes": ["Dragão", "Andrômeda", "Cisne", "Pégaso"],
        "resposta": "Andrômeda",
    },
    {
        "id": 8,
        "pergunta": "Qual é o signo representado pela primeira Casa do Zodíaco?",
        "opcoes": ["Touro", "Áries", "Gêmeos", "Leão"],
        "resposta": "Áries",
    },
]


def _usuario_autenticado():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return None
    try:
        usuario = db.session.get(Usuario, int(usuario_id))
    except (TypeError, ValueError):
        usuario = None
    if usuario is None:
        session.pop("usuario_id", None)
        session.pop("usuario_nome", None)
    return usuario


@desafios_bp.route("/desafios", methods=["GET", "POST"])
def desafios():
    usuario = _usuario_autenticado()
    if usuario is None:
        flash("Faça login para participar dos desafios do Santuário!", "warning")
        return redirect(url_for("login", next=url_for("desafios.desafios")))

    if session.get("desafio_usuario_id") != usuario.id:
        session.pop("ultimo_resultado_desafio", None)
        session["desafio_usuario_id"] = usuario.id

    if request.method == "POST":
        token_enviado = request.form.get("desafio_token", "")
        token_esperado = session.pop("desafio_token", None)
        if not token_esperado or not secrets.compare_digest(token_enviado, token_esperado):
            flash("Este desafio já foi enviado ou expirou. Inicie uma nova tentativa.", "warning")
            return redirect(url_for("desafios.desafios"))

        acertos = sum(
            request.form.get(f"resposta_{pergunta['id']}") == pergunta["resposta"]
            for pergunta in PERGUNTAS
        )
        total = len(PERGUNTAS)
        pontuacao = acertos * 10
        usuario.pontos = (usuario.pontos or 0) + pontuacao
        resultado = {
            "acertos": acertos,
            "total": total,
            "pontuacao": pontuacao,
            "porcentagem": round(acertos * 100 / total) if total else 0,
            "pontos_totais": usuario.pontos,
        }
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Não foi possível guardar sua pontuação. Tente novamente.", "danger")
            return redirect(url_for("desafios.desafios"))

        session["ultimo_resultado_desafio"] = resultado
        flash(f"Desafio concluído! Você conseguiu {acertos} de {total} acertos!", "success")
        return redirect(url_for("desafios.resultado_desafio"))

    token = session.get("desafio_token")
    if not token:
        token = secrets.token_urlsafe(24)
        session["desafio_token"] = token
    return render_template(
        "desafios.html",
        perguntas=PERGUNTAS,
        resultado=None,
        desafio_token=token,
    )


@desafios_bp.route("/desafios/resultado")
def resultado_desafio():
    usuario = _usuario_autenticado()
    if usuario is None:
        flash("Faça login para acessar seu resultado!", "warning")
        return redirect(url_for("login", next=url_for("desafios.resultado_desafio")))

    resultado = session.get("ultimo_resultado_desafio")
    if not resultado:
        flash("Você ainda não participou de nenhum desafio!", "info")
        return redirect(url_for("desafios.desafios"))

    return render_template("desafios.html", perguntas=PERGUNTAS, resultado=resultado)
