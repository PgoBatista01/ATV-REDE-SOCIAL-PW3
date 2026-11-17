
"""Rotas principais do Santuário Social."""

import os
import uuid

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from werkzeug.utils import secure_filename

from models.database import (
    Cavaleiro,
    Curiosidade,
    Imagem,
    PublicacaoCavaleiro,
    Usuario,
    db
)


EXTENSOES_IMAGEM = {"png", "jpg", "jpeg", "gif", "webp"}


# USUÁRIO ATUAL
def obter_usuario_atual():
    """Devolve o usuário atual da sessão."""

    usuario_id = session.get("usuario_id")

    if usuario_id is None:
        return None

    try:
        usuario_id = int(usuario_id)

    except (TypeError, ValueError):
        session.pop("usuario_id", None)
        session.pop("usuario_nome", None)
        return None

    usuario = db.session.get(Usuario, usuario_id)

    if usuario is None:
        session.pop("usuario_id", None)
        session.pop("usuario_nome", None)

    return usuario


# VALIDAR EXTENSÃO DA IMAGEM
def extensao_imagem_permitida(filename):

    nome_seguro = secure_filename(filename or "")

    return bool(
        nome_seguro
        and "." in nome_seguro
        and nome_seguro.rsplit(".", 1)[1].lower() in EXTENSOES_IMAGEM
    )


# GUARDAR IMAGEM
def guardar_imagem(upload, prefixo="imagem"):
    """Guarda uma imagem na pasta static/uploads."""

    if upload is None or not upload.filename:
        return None

    original = secure_filename(upload.filename)

    if not extensao_imagem_permitida(original):
        raise ValueError(
            "Formato de imagem inválido. Use PNG, JPG, JPEG, GIF ou WEBP."
        )

    extensao = original.rsplit(".", 1)[1].lower()
    filename = f"{prefixo}_{uuid.uuid4().hex}.{extensao}"

    pasta = current_app.config.get("UPLOAD_FOLDER")

    if not pasta:
        pasta = os.path.join(
            current_app.static_folder or "static",
            "uploads"
        )

        current_app.config["UPLOAD_FOLDER"] = pasta

    os.makedirs(pasta, exist_ok=True)

    upload.save(os.path.join(pasta, filename))

    return filename


# REGISTRAR ROTAS
def init_app(app):

    app.config.setdefault(
        "MAX_CONTENT_LENGTH",
        16 * 1024 * 1024
    )

    # INÍCIO
    @app.route("/")
    def index():

        cavaleiros = Cavaleiro.query.order_by(
            Cavaleiro.id.asc()
        ).limit(6).all()

        return render_template(
            "index.html",
            cavaleiros=cavaleiros,
            usuario=obter_usuario_atual()
        )

    app.add_url_rule(
        "/",
        endpoint="home",
        view_func=index
    )

    # CADASTRO
    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():

        if request.method == "POST":

            nome = request.form.get("nome", "").strip()
            nickname = request.form.get("nickname", "").strip()
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")
            confirmar = request.form.get("confirmar_senha", "")

            if not all((nome, nickname, email, senha)):

                flash(
                    "Preencha todos os campos obrigatórios.",
                    "danger"
                )

            elif len(senha) < 8:

                flash(
                    "A senha deve ter pelo menos 8 caracteres.",
                    "warning"
                )

            elif confirmar and senha != confirmar:

                flash(
                    "As senhas não coincidem.",
                    "danger"
                )

            elif Usuario.query.filter(
                or_(
                    Usuario.email == email,
                    Usuario.nickname == nickname
                )
            ).first():

                flash(
                    "Esse e-mail ou nickname já está registado.",
                    "danger"
                )

            else:

                usuario = Usuario(
                    nome=nome,
                    nickname=nickname,
                    email=email,
                    senha=generate_password_hash(senha)
                )

                db.session.add(usuario)

                try:
                    db.session.commit()

                except IntegrityError:
                    db.session.rollback()

                    flash(
                        "Esse e-mail ou nickname já está registado.",
                        "danger"
                    )

                else:

                    session.clear()

                    session["usuario_id"] = usuario.id
                    session["usuario_nome"] = usuario.nome

                    flash(
                        "Cadastro efetuado. Bem-vindo ao Santuário!",
                        "success"
                    )

                    return redirect(url_for("perfil"))

        return render_template("cadastro.html")

    # LOGIN
    @app.route("/login", methods=["GET", "POST"])
    def login():

        next_url = (
            request.args.get("next")
            or request.form.get("next")
        )

        if request.method == "POST":

            identificador = request.form.get(
                "identificador", ""
            ).strip()

            if not identificador:

                identificador = request.form.get(
                    "email",
                    request.form.get("nickname", "")
                ).strip()

            senha = request.form.get("senha", "")

            usuario = Usuario.query.filter(
                or_(
                    Usuario.email == identificador.lower(),
                    Usuario.nickname == identificador
                )
            ).first()

            if usuario and check_password_hash(
                usuario.senha,
                senha
            ):

                session.clear()

                session["usuario_id"] = usuario.id
                session["usuario_nome"] = usuario.nome

                flash(
                    f"Bem-vindo, {usuario.nickname}!",
                    "success"
                )

                if (
                    next_url
                    and next_url.startswith("/")
                    and not next_url.startswith("//")
                ):
                    return redirect(next_url)

                return redirect(url_for("perfil"))

            flash(
                "E-mail/nickname ou senha incorretos.",
                "danger"
            )

        return render_template(
            "login.html",
            next=next_url
        )

    # SAIR
    @app.route("/logout", methods=["GET", "POST"])
    def logout():

        session.clear()

        flash(
            "Sessão terminada.",
            "info"
        )

        return redirect(url_for("index"))

    # PERFIL DO USUÁRIO
    @app.route("/perfil", methods=["GET", "POST"])
    def perfil():

        usuario = obter_usuario_atual()

        if usuario is None:

            flash(
                "Inicie sessão para aceder ao perfil.",
                "warning"
            )

            return redirect(
                url_for(
                    "login",
                    next=url_for("perfil")
                )
            )

        if request.method == "POST":

            nome = request.form.get(
                "nome",
                usuario.nome
            ).strip()

            if not nome:

                flash(
                    "O nome não pode ficar vazio.",
                    "warning"
                )

                return redirect(url_for("perfil"))

            usuario.nome = nome

            usuario.biografia = (
                request.form.get("biografia", "").strip() or None
            )

            usuario.personagem_favorito = (
                request.form.get(
                    "personagem_favorito",
                    ""
                ).strip() or None
            )

            usuario.carta_favorita = (
                request.form.get(
                    "carta_favorita",
                    ""
                ).strip() or None
            )

            foto = request.files.get("foto_perfil")

            if foto and foto.filename:

                try:
                    usuario.foto_perfil = guardar_imagem(
                        foto,
                        "perfil"
                    )

                except ValueError as exc:

                    flash(str(exc), "danger")

                    return redirect(url_for("perfil"))

            try:
                db.session.commit()

            except IntegrityError:

                db.session.rollback()

                flash(
                    "Não foi possível atualizar o perfil.",
                    "danger"
                )

            else:

                session["usuario_nome"] = usuario.nome

                flash(
                    "Perfil atualizado com sucesso.",
                    "success"
                )

            return redirect(url_for("perfil"))

        return render_template(
            "perfil.html",
            usuario=usuario
        )

    # ENCICLOPÉDIA
    @app.route("/enciclopedia")
    def enciclopedia():

        cavaleiros = Cavaleiro.query.order_by(
            Cavaleiro.id.asc()
        ).all()

        curiosidades = Curiosidade.query.order_by(
            Curiosidade.id.asc()
        ).all()

        return render_template(
            "enciclopedia.html",
            cavaleiros=cavaleiros,
            curiosidades=curiosidades
        )

    # CASAS DO ZODÍACO
    @app.route("/casas")
    @app.route("/doze-casas")
    def casas():

        return render_template("casas.html")

    # PERSONAGENS
    @app.route("/personagens")
    @app.route("/cavaleiros")
    def personagens():

        return redirect(url_for("enciclopedia"))

    # PERFIL INDIVIDUAL DO CAVALEIRO
    @app.route(
        "/perfil-cavaleiro/<int:cavaleiro_id>",
        endpoint="perfil_cavaleiro"
    )
    @app.route("/cavaleiro/<int:cavaleiro_id>")
    def detalhe_cavaleiro(cavaleiro_id):

        cavaleiro = db.session.get(
            Cavaleiro,
            cavaleiro_id
        )

        if cavaleiro is None:
            abort(404)

        # PUBLICAÇÕES DO CAVALEIRO
        publicacoes = PublicacaoCavaleiro.query.filter_by(
            cavaleiro_id=cavaleiro.id
        ).order_by(
            PublicacaoCavaleiro.data.desc(),
            PublicacaoCavaleiro.id.desc()
        ).all()

        return render_template(
            "perfil_cavaleiros.html",
            cavaleiro=cavaleiro,
            publicacoes=publicacoes,
            usuario=obter_usuario_atual()
        )

    # FEED DO SANTUÁRIO
    @app.route("/feed")
    def feed():

        # PUBLICAÇÕES DOS CAVALEIROS
        publicacoes = PublicacaoCavaleiro.query.order_by(
            PublicacaoCavaleiro.data.desc(),
            PublicacaoCavaleiro.id.desc()
        ).all()

        # PUBLICAÇÕES DOS USUÁRIOS
        publicacoes_usuarios = Imagem.query.order_by(
            Imagem.data.desc(),
            Imagem.id.desc()
        ).all()

        return render_template(
            "feed.html",
            publicacoes=publicacoes,
            publicacoes_usuarios=publicacoes_usuarios,
            usuario=obter_usuario_atual()
        )

    # GALERIA
    @app.route("/galeria", methods=["GET", "POST"])
    def galeria():

        usuario = obter_usuario_atual()

        if request.method == "POST":

            if usuario is None:

                flash(
                    "Inicie sessão para publicar uma imagem.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "login",
                        next=url_for("galeria")
                    )
                )

            upload = (
                request.files.get("file")
                or request.files.get("imagem")
            )

            legenda = request.form.get(
                "legenda",
                ""
            ).strip()

            if upload is None or not upload.filename:

                flash(
                    "Selecione uma imagem para publicar.",
                    "warning"
                )

            elif len(legenda) > 500:

                flash(
                    "A legenda não pode exceder 500 caracteres.",
                    "warning"
                )

            else:

                try:
                    filename = guardar_imagem(
                        upload,
                        "galeria"
                    )

                except ValueError as exc:

                    flash(str(exc), "danger")

                else:

                    imagem = Imagem(
                        filename=filename,
                        legenda=legenda or None,
                        usuario_id=usuario.id
                    )

                    db.session.add(imagem)

                    try:
                        db.session.commit()

                    except IntegrityError:

                        db.session.rollback()

                        caminho = os.path.join(
                            current_app.config["UPLOAD_FOLDER"],
                            filename
                        )

                        if os.path.exists(caminho):
                            os.remove(caminho)

                        flash(
                            "Não foi possível guardar a imagem.",
                            "danger"
                        )

                    else:

                        flash(
                            "Imagem publicada na galeria.",
                            "success"
                        )

                        return redirect(url_for("galeria"))

        imagens = Imagem.query.order_by(
            Imagem.data.desc(),
            Imagem.id.desc()
        ).all()

        return render_template(
            "galeria.html",
            imagens=imagens,
            usuario=usuario
        )

    # EXCLUIR PUBLICAÇÃO DA GALERIA
    @app.post("/galeria/excluir/<int:id>")
    def excluir_imagem(id):

        usuario = obter_usuario_atual()

        if usuario is None:

            flash(
                "Inicie sessão para excluir uma publicação.",
                "warning"
            )

            return redirect(
                url_for(
                    "login",
                    next=url_for("galeria")
                )
            )

        imagem = db.session.get(
            Imagem,
            id
        )

        if imagem is None:
            abort(404)

        if imagem.usuario_id != usuario.id:
            abort(403)

        filename = secure_filename(
            imagem.filename or ""
        )

        pasta = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(
                current_app.static_folder,
                "uploads"
            )
        )

        caminho = os.path.join(
            pasta,
            filename
        )

        db.session.delete(imagem)
        db.session.commit()

        if filename and os.path.isfile(caminho):
            os.remove(caminho)

        flash(
            "Publicação excluída.",
            "success"
        )

        return redirect(url_for("galeria"))

    # RANKING
    @app.route("/ranking")
    def ranking():

        usuarios = Usuario.query.order_by(
            Usuario.pontos.desc(),
            Usuario.nickname.asc()
        ).limit(50).all()

        return render_template(
            "ranking.html",
            usuarios=usuarios
        )

    # CHAT
    @app.route("/chat", methods=["GET", "POST"])
    def chat_page():

        if obter_usuario_atual() is None:

            flash(
                "Inicie sessão para entrar no chat.",
                "warning"
            )

            return redirect(
                url_for(
                    "login",
                    next=url_for("chat_page")
                )
            )

        return render_template("chat.html")

    # QUIZ
    @app.route("/quiz", methods=["GET", "POST"])
    def quiz_alias():

        return redirect(
            url_for("desafios.desafios")
        )
