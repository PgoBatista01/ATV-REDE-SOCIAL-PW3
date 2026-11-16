
# IMPORTANDO BIBLIOTECAS DO FLASK
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

# IMPORTANDO OS MODELOS DO BANCO
from models.database import (
    db,
    Cavaleiro,
    Curiosidade,
    Usuario,
    Imagem
)

# CRIPTOGRAFIA DE SENHAS
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# MANIPULACAO DE ARQUIVOS
import os
import uuid
from werkzeug.utils import secure_filename


# ==========================================================
# FUNCAO PRINCIPAL PARA INICIALIZAR AS ROTAS
# ==========================================================

def init_app(app):

    # CONFIGURACAO DA PASTA DE UPLOAD
    app.config.setdefault(
        'UPLOAD_FOLDER',
        os.path.join(app.static_folder, 'uploads')
    )

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # EXTENSOES PERMITIDAS
    EXTENSOES_PERMITIDAS = {
        'png', 'jpg', 'jpeg', 'gif', 'webp'
    }

    def arquivo_permitido(filename):
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower()
            in EXTENSOES_PERMITIDAS
        )

    # ======================================================
    # MIDDLEWARE DE AUTENTICACAO
    # ======================================================

    @app.before_request
    def check_auth():

        rotas_permitidas = [
            'home',
            'login',
            'cadastro',
            'static'
        ]

        if request.endpoint in rotas_permitidas:
            return

        if 'usuario_id' not in session:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))

    # ======================================================
    # ROTA HOME
    # ======================================================

    @app.route('/')
    def home():

        return render_template('index.html')

    # ======================================================
    # ROTA ENCICLOPEDIA
    # ======================================================

    @app.route('/enciclopedia')
    def enciclopedia():

        cavaleiros = Cavaleiro.query.order_by(
            Cavaleiro.nome
        ).all()

        curiosidades = Curiosidade.query.all()

        return render_template(
            'enciclopedia.html',
            cavaleiros=cavaleiros,
            curiosidades=curiosidades
        )

    # ======================================================
    # ROTA DAS DOZE CASAS
    # ======================================================

    @app.route('/casas')
    def casas():

        return render_template('casas.html')

    # ======================================================
    # ROTA DO CHAT
    # ======================================================

    @app.route('/chat')
    def chat_page():

        nickname = session.get('usuario_nickname')

        return render_template(
            'chat.html',
            nickname=nickname
        )

    # ======================================================
    # ROTA DE CADASTRO
    # ======================================================

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():

        if request.method == 'POST':

            nome = request.form.get('nome', '').strip()
            nickname = request.form.get('nickname', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')

            if not nome or not nickname or not email or not senha:
                flash('Preencha todos os campos.', 'danger')
                return redirect(url_for('cadastro'))

            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
                return redirect(url_for('cadastro'))

            usuario_existente = Usuario.query.filter(
                (Usuario.email == email) |
                (Usuario.nickname == nickname)
            ).first()

            if usuario_existente:
                flash('E-mail ou nickname já cadastrado.', 'danger')
                return redirect(url_for('cadastro'))

            senha_hash = generate_password_hash(
                senha,
                method='scrypt'
            )

            novo_usuario = Usuario(
                nome=nome,
                nickname=nickname,
                email=email,
                senha=senha_hash
            )

            try:
                db.session.add(novo_usuario)
                db.session.commit()

                flash('Cadastro realizado com sucesso! Faça seu login.', 'success')
                return redirect(url_for('login'))

            except Exception:
                db.session.rollback()
                flash('Não foi possível realizar o cadastro.', 'danger')

        return render_template('cadastro.html')

    # ======================================================
    # ROTA DE LOGIN
    # ======================================================

    @app.route('/login', methods=['GET', 'POST'])
    def login():

        if request.method == 'POST':

            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')

            usuario = Usuario.query.filter_by(
                email=email
            ).first()

            if usuario and check_password_hash(usuario.senha, senha):

                session.clear()

                session['usuario_id'] = usuario.id
                session['usuario_nome'] = usuario.nome
                session['usuario_email'] = usuario.email
                session['usuario_nickname'] = usuario.nickname

                flash('Login realizado com sucesso!', 'success')

                return redirect(url_for('home'))

            flash('E-mail ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

        return render_template('login.html')

    # ======================================================
    # ROTA DE PERFIL
    # ======================================================

    @app.route('/perfil', methods=['GET', 'POST'])
    def perfil():

        usuario = Usuario.query.get(session['usuario_id'])

        if not usuario:
            session.clear()
            flash('Usuário não encontrado. Faça login novamente.', 'danger')
            return redirect(url_for('login'))

        if request.method == 'POST':

            nome = request.form.get('nome', '').strip()
            biografia = request.form.get('biografia', '').strip()
            personagem = request.form.get('personagem_favorito', '').strip()
            carta = request.form.get('carta_favorita', '').strip()

            if not nome:
                flash('O nome não pode ficar vazio.', 'danger')
                return redirect(url_for('perfil'))

            usuario.nome = nome
            usuario.biografia = biografia
            usuario.personagem_favorito = personagem
            usuario.carta_favorita = carta

            foto = request.files.get('foto_perfil')

            if foto and foto.filename:

                if not arquivo_permitido(foto.filename):
                    flash('Formato de imagem não permitido.', 'danger')
                    return redirect(url_for('perfil'))

                extensao = secure_filename(foto.filename).rsplit('.', 1)[1].lower()
                novo_nome = f'{uuid.uuid4().hex}.{extensao}'

                caminho = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    novo_nome
                )

                foto.save(caminho)

                usuario.foto_perfil = novo_nome

            try:
                db.session.commit()

                session['usuario_nome'] = usuario.nome

                flash('Perfil atualizado com sucesso!', 'success')
                return redirect(url_for('perfil'))

            except Exception:
                db.session.rollback()
                flash('Não foi possível atualizar o perfil.', 'danger')

        return render_template(
            'perfil.html',
            usuario=usuario
        )

    # ======================================================
    # ROTA DO RANKING
    # ======================================================

    @app.route('/ranking')
    def ranking():

        usuarios = Usuario.query.order_by(
            Usuario.pontos.desc(),
            Usuario.nome.asc()
        ).all()

        return render_template(
            'ranking.html',
            usuarios=usuarios
        )

    # ======================================================
    # ROTA DA GALERIA
    # ======================================================

    @app.route('/galeria', methods=['GET', 'POST'])
    def galeria():

        if request.method == 'POST':

            arquivo = request.files.get('file')
            legenda = request.form.get('legenda', '').strip()

            if not arquivo or not arquivo.filename:
                flash('Selecione uma imagem.', 'danger')
                return redirect(url_for('galeria'))

            if not arquivo_permitido(arquivo.filename):
                flash('Formato de imagem não permitido.', 'danger')
                return redirect(url_for('galeria'))

            extensao = secure_filename(arquivo.filename).rsplit('.', 1)[1].lower()
            filename = f'{uuid.uuid4().hex}.{extensao}'

            caminho = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            try:
                arquivo.save(caminho)

                imagem = Imagem(
                    filename=filename,
                    legenda=legenda,
                    usuario_id=session['usuario_id']
                )

                db.session.add(imagem)
                db.session.commit()

                flash('Imagem publicada com sucesso!', 'success')

            except Exception:
                db.session.rollback()

                if os.path.exists(caminho):
                    os.remove(caminho)

                flash('Não foi possível publicar a imagem.', 'danger')

            return redirect(url_for('galeria'))

        imagens = Imagem.query.order_by(
            Imagem.data.desc()
        ).all()

        return render_template(
            'galeria.html',
            imagens=imagens
        )

    # ======================================================
    # ROTA PARA EXCLUIR UMA IMAGEM
    # ======================================================

    @app.route('/galeria/excluir/<int:id>', methods=['POST'])
    def excluir_imagem(id):

        imagem = Imagem.query.get_or_404(id)

        if imagem.usuario_id != session['usuario_id']:
            flash('Você não pode excluir esta publicação.', 'danger')
            return redirect(url_for('galeria'))

        caminho = os.path.join(
            app.config['UPLOAD_FOLDER'],
            imagem.filename
        )

        try:
            db.session.delete(imagem)
            db.session.commit()

            if os.path.exists(caminho):
                os.remove(caminho)

            flash('Publicação excluída com sucesso!', 'success')

        except Exception:
            db.session.rollback()
            flash('Não foi possível excluir a publicação.', 'danger')

        return redirect(url_for('galeria'))

    # ======================================================
    # ROTA DE LOGOUT
    # ======================================================

    @app.route('/logout')
    def logout():

        session.clear()

        flash('Você saiu da sua conta.', 'success')

        return redirect(url_for('home'))
