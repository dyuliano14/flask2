"""
Rotas para gerenciamento de conteúdos e flashcards.

Este módulo contém todas as rotas relacionadas ao CRUD de conteúdos
(PDFs, markdown, vídeos) e flashcards do sistema de estudos.
"""

import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.models.user import db
from src.models.estudo import Conteudo, Flashcard, Materia
from datetime import datetime, timedelta
import uuid

# Criação do blueprint para as rotas de conteúdos
conteudos_bp = Blueprint("conteudos", __name__)

# Configurações para upload de arquivos
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "mp4", "avi", "mov", "wmv", "flv", "webm"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_upload_folder():
    """Cria a pasta de uploads se não existir."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    return UPLOAD_FOLDER


# ===== ROTAS PARA CONTEÚDOS =====


@conteudos_bp.route("/materias/<int:materia_id>/conteudos", methods=["GET"])
def listar_conteudos(materia_id):
    """
    Lista todos os conteúdos de uma matéria.

    Args:
        materia_id (int): ID da matéria

    Returns:
        JSON: Lista de conteúdos da matéria
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                "success": False,
                "message": "Matéria não encontrada"
            }), 404

        conteudos = Conteudo.query.filter_by(materia_id=materia_id).order_by(
            Conteudo.ordem, Conteudo.data_criacao).all()

        return jsonify({
            "success":
            True,
            "conteudos": [conteudo.to_dict() for conteudo in conteudos]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar conteúdos: {str(e)}"
        }), 500


@conteudos_bp.route("/materias/<int:materia_id>/conteudos", methods=["POST"])
def criar_conteudo(materia_id):
    """
    Cria um novo conteúdo em uma matéria.

    Args:
        materia_id (int): ID da matéria

    Para conteúdo de texto/markdown:
    Expected JSON:
        {
            "titulo": "Título do conteúdo",
            "tipo": "markdown",
            "conteudo_texto": "Conteúdo em markdown..."
        }

    Para upload de arquivo:
    Expected form-data:
        - titulo: Título do conteúdo
        - tipo: "pdf" ou "video"
        - arquivo: Arquivo a ser enviado

    Returns:
        JSON: Dados do conteúdo criado
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                "success": False,
                "message": "Matéria não encontrada"
            }), 404

        # Verificar se é upload de arquivo ou conteúdo de texto
        if request.content_type and "multipart/form-data" in request.content_type:
            # Upload de arquivo
            titulo = request.form.get("titulo")
            tipo = request.form.get("tipo")

            if not titulo or not tipo:
                return jsonify({
                    "success": False,
                    "message": "Título e tipo são obrigatórios"
                }), 400

            if "arquivo" not in request.files:
                return jsonify({
                    "success": False,
                    "message": "Nenhum arquivo foi enviado"
                }), 400

            arquivo = request.files["arquivo"]

            if arquivo.filename == "":
                return jsonify({
                    "success": False,
                    "message": "Nenhum arquivo foi selecionado"
                }), 400

            if arquivo and allowed_file(arquivo.filename):
                # Criar nome único para o arquivo
                filename = secure_filename(arquivo.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"

                # Criar pasta de uploads
                upload_path = create_upload_folder()
                file_path = os.path.join(upload_path, unique_filename)

                # Salvar arquivo
                arquivo.save(file_path)

                # Obter a próxima ordem
                ultima_ordem = db.session.query(db.func.max(
                    Conteudo.ordem)).filter_by(
                        materia_id=materia_id).scalar() or 0

                novo_conteudo = Conteudo(titulo=titulo,
                                         tipo=tipo,
                                         arquivo_path=file_path,
                                         materia_id=materia_id,
                                         ordem=ultima_ordem + 1)

                db.session.add(novo_conteudo)
                db.session.commit()

                return jsonify({
                    "success": True,
                    "message": "Conteúdo criado com sucesso",
                    "conteudo": novo_conteudo.to_dict()
                }), 201
            else:
                return jsonify({
                    "success": False,
                    "message": "Tipo de arquivo não permitido"
                }), 400

        else:
            # Conteúdo de texto/markdown
            dados = request.get_json()

            if not dados or "titulo" not in dados or "tipo" not in dados:
                return jsonify({
                    "success": False,
                    "message": "Título e tipo são obrigatórios"
                }), 400

            if dados["tipo"] == "markdown" and "conteudo_texto" not in dados:
                return jsonify({
                    "success":
                    False,
                    "message":
                    "Conteúdo de texto é obrigatório para tipo markdown"
                }), 400

            # Obter a próxima ordem
            ultima_ordem = db.session.query(db.func.max(
                Conteudo.ordem)).filter_by(materia_id=materia_id).scalar() or 0

            novo_conteudo = Conteudo(titulo=dados["titulo"],
                                     tipo=dados["tipo"],
                                     conteudo_texto=dados.get(
                                         "conteudo_texto", ""),
                                     materia_id=materia_id,
                                     ordem=ultima_ordem + 1)

            db.session.add(novo_conteudo)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Conteúdo criado com sucesso",
                "conteudo": novo_conteudo.to_dict()
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao criar conteúdo: {str(e)}"
        }), 500


@conteudos_bp.route("/conteudos/<int:conteudo_id>", methods=["GET"])
def obter_conteudo(conteudo_id):
    """
    Obtém um conteúdo específico.

    Args:
        conteudo_id (int): ID do conteúdo

    Returns:
        JSON: Dados completos do conteúdo
    """
    try:
        conteudo = Conteudo.query.get_or_404(conteudo_id)

        return jsonify({"success": True, "conteudo": conteudo.to_dict()}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao obter conteúdo: {str(e)}"
        }), 500


@conteudos_bp.route("/conteudos/<int:conteudo_id>", methods=["PUT"])
def atualizar_conteudo(conteudo_id):
    """
    Atualiza um conteúdo existente.

    Args:
        conteudo_id (int): ID do conteúdo

    Para conteúdo de texto/markdown:
    Expected JSON:
        {
            "titulo": "Novo título",
            "tipo": "markdown",
            "conteudo_texto": "Novo conteúdo em markdown..."
        }

    Para upload de arquivo (substituir arquivo ou apenas atualizar metadados):
    Expected form-data:
        - titulo: Novo título
        - tipo: "pdf" ou "video"
        - arquivo: Novo arquivo a ser enviado (opcional)

    Returns:
        JSON: Dados do conteúdo atualizado
    """
    try:
        conteudo = Conteudo.query.get_or_404(conteudo_id)

        if request.content_type and "multipart/form-data" in request.content_type:
            # Atualização com arquivo (pode ser substituição ou apenas metadados)
            titulo = request.form.get("titulo")
            tipo = request.form.get("tipo")
            arquivo = request.files.get("arquivo")

            if titulo: conteudo.titulo = titulo
            if tipo: conteudo.tipo = tipo

            if arquivo and arquivo.filename != ":::":  # Verifica se um novo arquivo foi enviado
                if not allowed_file(arquivo.filename):
                    return jsonify({
                        "success": False,
                        "message": "Tipo de arquivo não permitido"
                    }), 400

                # Remover arquivo antigo se existir
                if conteudo.arquivo_path and os.path.exists(
                        conteudo.arquivo_path):
                    os.remove(conteudo.arquivo_path)

                filename = secure_filename(arquivo.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                arquivo.save(file_path)
                conteudo.arquivo_path = file_path
                conteudo.conteudo_texto = None  # Limpa texto se for arquivo

        else:
            # Atualização de conteúdo de texto/markdown ou metadados sem arquivo
            dados = request.get_json()
            if not dados:
                return jsonify({
                    "success": False,
                    "message": "Dados inválidos"
                }), 400

            if "titulo" in dados: conteudo.titulo = dados["titulo"]
            if "tipo" in dados: conteudo.tipo = dados["tipo"]

            if conteudo.tipo == "markdown":
                if "conteudo_texto" in dados:
                    conteudo.conteudo_texto = dados["conteudo_texto"]
                conteudo.arquivo_path = None  # Limpa path se for texto
            else:
                # Se o tipo mudou para arquivo, e não há arquivo novo, o path existente permanece
                # Se o tipo mudou para arquivo e havia texto, o texto é limpo
                conteudo.conteudo_texto = None

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Conteúdo atualizado com sucesso",
            "conteudo": conteudo.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar conteúdo: {str(e)}"
        }), 500


@conteudos_bp.route("/conteudos/<int:conteudo_id>", methods=["DELETE"])
def deletar_conteudo(conteudo_id):
    """
    Deleta um conteúdo específico.

    Args:
        conteudo_id (int): ID do conteúdo

    Returns:
        JSON: Confirmação da exclusão
    """
    try:
        conteudo = Conteudo.query.get_or_404(conteudo_id)

        # Remover arquivo físico se existir
        if conteudo.arquivo_path and os.path.exists(conteudo.arquivo_path):
            os.remove(conteudo.arquivo_path)

        db.session.delete(conteudo)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Conteúdo deletado com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao deletar conteúdo: {str(e)}"
        }), 500


@conteudos_bp.route("/conteudos/<int:conteudo_id>/download", methods=["GET"])
def download_conteudo(conteudo_id):
    """
    Faz download de um arquivo de conteúdo.

    Args:
        conteudo_id (int): ID do conteúdo

    Returns:
        File: Arquivo para download
    """
    try:
        conteudo = Conteudo.query.get_or_404(conteudo_id)

        if not conteudo.arquivo_path or not os.path.exists(
                conteudo.arquivo_path):
            return jsonify({
                "success": False,
                "message": "Arquivo não encontrado"
            }), 404

        # Extrair o nome original do arquivo para o download
        original_filename = os.path.basename(conteudo.arquivo_path).split(
            "_", 1)[-1]

        return send_file(conteudo.arquivo_path,
                         as_attachment=True,
                         download_name=original_filename)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao fazer download: {str(e)}"
        }), 500


@conteudos_bp.route("/conteudos/<int:conteudo_id>/marcar-estudado",
                    methods=["PUT"])
def marcar_estudado(conteudo_id):
    """
    Marca um conteúdo como estudado.

    Args:
        conteudo_id (int): ID do conteúdo

    Returns:
        JSON: Confirmação da atualização
    """
    try:
        conteudo = Conteudo.query.get_or_404(conteudo_id)

        conteudo.estudado = True
        conteudo.data_estudo = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Conteúdo marcado como estudado",
            "conteudo": conteudo.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao marcar conteúdo: {str(e)}"
        }), 500


# ===== ROTAS PARA FLASHCARDS =====


@conteudos_bp.route("/materias/<int:materia_id>/flashcards", methods=["GET"])
def listar_flashcards(materia_id):
    """
    Lista todos os flashcards de uma matéria.

    Args:
        materia_id (int): ID da matéria

    Returns:
        JSON: Lista de flashcards da matéria
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                "success": False,
                "message": "Matéria não encontrada"
            }), 404

        flashcards = Flashcard.query.filter_by(
            materia_id=materia_id,
            ativo=True).order_by(Flashcard.data_criacao.desc()).all()

        return jsonify({
            "success":
            True,
            "flashcards": [flashcard.to_dict() for flashcard in flashcards]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar flashcards: {str(e)}"
        }), 500


@conteudos_bp.route("/materias/<int:materia_id>/flashcards", methods=["POST"])
def criar_flashcard(materia_id):
    """
    Cria um novo flashcard em uma matéria.

    Args:
        materia_id (int): ID da matéria

    Expected JSON:
        {
            "pergunta": "Pergunta do flashcard",
            "resposta": "Resposta do flashcard",
            "dificuldade": 1  # 1=fácil, 2=médio, 3=difícil (opcional, padrão=1)
        }

    Returns:
        JSON: Dados do flashcard criado
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                "success": False,
                "message": "Matéria não encontrada"
            }), 404

        dados = request.get_json()

        if not dados or "pergunta" not in dados or "resposta" not in dados:
            return jsonify({
                "success": False,
                "message": "Pergunta e resposta são obrigatórias"
            }), 400

        # Calcular próxima revisão (1 dia para novos flashcards)
        proxima_revisao = datetime.utcnow() + timedelta(days=1)

        novo_flashcard = Flashcard(pergunta=dados["pergunta"],
                                   resposta=dados["resposta"],
                                   dificuldade=dados.get("dificuldade", 1),
                                   materia_id=materia_id,
                                   proxima_revisao=proxima_revisao)

        db.session.add(novo_flashcard)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Flashcard criado com sucesso",
            "flashcard": novo_flashcard.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao criar flashcard: {str(e)}"
        }), 500


@conteudos_bp.route("/flashcards/<int:flashcard_id>/responder",
                    methods=["PUT"])
def responder_flashcard(flashcard_id):
    """
    Registra a resposta a um flashcard e atualiza o algoritmo de repetição espaçada.

    Args:
        flashcard_id (int): ID do flashcard

    Expected JSON:
        {
            "acertou": true/false
        }

    Returns:
        JSON: Dados atualizados do flashcard
    """
    try:
        flashcard = Flashcard.query.get_or_404(flashcard_id)
        dados = request.get_json()

        if not dados or "acertou" not in dados:
            return jsonify({
                "success": False,
                "message": "Campo \"acertou\" é obrigatório"
            }), 400

        acertou = dados["acertou"]

        # Atualizar contadores
        if acertou:
            flashcard.acertos += 1
        else:
            flashcard.erros += 1

        # Atualizar data da última revisão
        flashcard.ultima_revisao = datetime.utcnow()

        # Algoritmo simples de repetição espaçada
        if acertou:
            # Se acertou, aumenta o intervalo baseado na dificuldade e histórico
            if flashcard.acertos == 1:
                dias = 1
            elif flashcard.acertos == 2:
                dias = 3
            elif flashcard.acertos == 3:
                dias = 7
            else:
                dias = min(30, flashcard.acertos * 3)  # Máximo de 30 dias

            # Ajustar baseado na dificuldade
            if flashcard.dificuldade == 3:  # Difícil
                dias = max(1, dias // 2)
            elif flashcard.dificuldade == 1:  # Fácil
                dias = min(60, dias * 2)
        else:
            # Se errou, volta para 1 dia
            dias = 1
            flashcard.acertos = 0  # Reset dos acertos

        flashcard.proxima_revisao = datetime.utcnow() + timedelta(days=dias)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Resposta registrada com sucesso",
            "flashcard": flashcard.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao registrar resposta: {str(e)}"
        }), 500


@conteudos_bp.route("/flashcards/revisar", methods=["GET"])
def flashcards_para_revisar():
    """
    Obtém flashcards que estão prontos para revisão.

    Query params:
        - materia_id (opcional): Filtrar por matéria específica
        - limite (opcional): Número máximo de flashcards (padrão: 20)

    Returns:
        JSON: Lista de flashcards para revisar
    """
    try:
        materia_id = request.args.get("materia_id", type=int)
        limite = request.args.get("limite", default=20, type=int)

        query = Flashcard.query.filter(
            Flashcard.ativo == True, Flashcard.proxima_revisao
            <= datetime.utcnow())

        if materia_id:
            query = query.filter(Flashcard.materia_id == materia_id)

        flashcards = query.order_by(
            Flashcard.proxima_revisao).limit(limite).all()

        return jsonify({
            "success":
            True,
            "flashcards": [flashcard.to_dict() for flashcard in flashcards],
            "total":
            len(flashcards)
        }), 200

    except Exception as e:
        return jsonify({
            "success":
            False,
            "message":
            f"Erro ao obter flashcards para revisão: {str(e)}"
        }), 500


@conteudos_bp.route("/flashcards/<int:flashcard_id>", methods=["PUT"])
def atualizar_flashcard(flashcard_id):
    """
    Atualiza um flashcard existente.

    Args:
        flashcard_id (int): ID do flashcard

    Expected JSON:
        {
            "pergunta": "Nova pergunta",
            "resposta": "Nova resposta",
            "dificuldade": 2  # Opcional
        }

    Returns:
        JSON: Dados do flashcard atualizado
    """
    try:
        flashcard = Flashcard.query.get_or_404(flashcard_id)
        dados = request.get_json()

        if not dados:
            return jsonify({
                "success": False,
                "message": "Dados inválidos"
            }), 400

        if "pergunta" in dados: flashcard.pergunta = dados["pergunta"]
        if "resposta" in dados: flashcard.resposta = dados["resposta"]
        if "dificuldade" in dados: flashcard.dificuldade = dados["dificuldade"]

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Flashcard atualizado com sucesso",
            "flashcard": flashcard.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar flashcard: {str(e)}"
        }), 500


@conteudos_bp.route("/flashcards/<int:flashcard_id>", methods=["DELETE"])
def deletar_flashcard(flashcard_id):
    """
    Deleta um flashcard específico.

    Args:
        flashcard_id (int): ID do flashcard

    Returns:
        JSON: Confirmação da exclusão
    """
    try:
        flashcard = Flashcard.query.get_or_404(flashcard_id)

        db.session.delete(flashcard)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Flashcard deletado com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao deletar flashcard: {str(e)}"
        }), 500
