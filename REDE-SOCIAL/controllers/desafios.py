
from flask import Blueprint, render_template, request, session, redirect, url_for, flash


desafios_bp = Blueprint("desafios", __name__)


# BANCO DE PERGUNTAS
PERGUNTAS = [
    {
        "id": 1,
        "pergunta": "Qual é o cavaleiro de bronze conhecido pela Armadura de Pégaso?",
        "opcoes": ["Shiryu", "Seiya", "Hyoga", "Shun"],
        "resposta": "Seiya"
    },
    {
        "id": 2,
        "pergunta": "Qual é o nome da deusa que os cavaleiros protegem?",
        "opcoes": ["Ártemis", "Afrodite", "Atena", "Hera"],
        "resposta": "Atena"
    },
    {
        "id": 3,
        "pergunta": "Qual cavaleiro utiliza a Armadura de Dragão?",
        "opcoes": ["Ikki", "Shiryu", "Seiya", "Hyoga"],
        "resposta": "Shiryu"
    },
    {
        "id": 4,
        "pergunta": "Qual é o cavaleiro de bronze associado ao Cisne?",
        "opcoes": ["Shun", "Hyoga", "Ikki", "Shiryu"],
        "resposta": "Hyoga"
    },
    {
        "id": 5,
        "pergunta": "Qual é o nome do cavaleiro de Fênix?",
        "opcoes": ["Ikki", "Seiya", "Shun", "Hyoga"],
        "resposta": "Ikki"
    },
    {
        "id": 6,
        "pergunta": "Quantas são as Casas do Zodíaco no Santuário?",
        "opcoes": ["7", "10", "12", "15"],
        "resposta": "12"
    },
    {
        "id": 7,
        "pergunta": "Qual é a armadura de Shun?",
        "opcoes": ["Dragão", "Andrômeda", "Cisne", "Pégaso"],
        "resposta": "Andrômeda"
    },
    {
        "id": 8,
        "pergunta": "Qual é o signo representado pela primeira Casa do Zodíaco?",
        "opcoes": ["Touro", "Áries", "Gêmeos", "Leão"],
        "resposta": "Áries"
    }
]


# PAGINA DE DESAFIOS
@desafios_bp.route("/desafios", methods=["GET", "POST"])
def desafios():

    if not session.get("usuario_id"):
        flash("Faça login para participar dos desafios do Santuário!", "warning")
        return redirect(url_for("login"))

    resultado = None

    if request.method == "POST":

        acertos = 0
        total = len(PERGUNTAS)

        for pergunta in PERGUNTAS:

            resposta_usuario = request.form.get(
                f"resposta_{pergunta['id']}"
            )

            if resposta_usuario == pergunta["resposta"]:
                acertos += 1

        pontuacao = acertos * 10

        resultado = {
            "acertos": acertos,
            "total": total,
            "pontuacao": pontuacao,
            "porcentagem": round((acertos / total) * 100)
        }

        # EXPERIENCIA DO COSMO NA SESSAO
        session["ultimo_resultado_desafio"] = resultado

        flash(
            f"Desafio concluído! Você conseguiu {acertos} de {total} acertos!",
            "success"
        )

    return render_template(
        "desafios.html",
        perguntas=PERGUNTAS,
        resultado=resultado
    )


# CONSULTAR ULTIMO RESULTADO
@desafios_bp.route("/desafios/resultado")
def resultado_desafio():

    if not session.get("usuario_id"):
        flash("Faça login para acessar seu resultado!", "warning")
        return redirect(url_for("login"))

    resultado = session.get("ultimo_resultado_desafio")

    if not resultado:
        flash("Você ainda não participou de nenhum desafio!", "info")
        return redirect(url_for("desafios.desafios"))

    return render_template(
        "desafios.html",
        perguntas=PERGUNTAS,
        resultado=resultado
    )
