"""
Rotas para gerenciamento de cursos e matérias.

Este módulo contém todas as rotas relacionadas ao CRUD (Create, Read, Update, Delete)
de cursos e matérias no sistema de estudos.
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.estudo import Curso, Materia
from datetime import datetime

# Criação do blueprint para as rotas de cursos
cursos_bp = Blueprint("cursos", __name__)


@cursos_bp.route("/cursos", methods=["GET"])
def listar_cursos():
    """
    Lista todos os cursos ativos.

    Returns:
        JSON: Lista de cursos com suas informações básicas
    """
    try:
        cursos = Curso.query.filter_by(ativo=True).order_by(
            Curso.data_criacao.desc()).all()
        return jsonify({
            "success": True,
            "cursos": [curso.to_dict() for curso in cursos]
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar cursos: {str(e)}"
        }), 500


@cursos_bp.route("/cursos", methods=["POST"])
def criar_curso():
    """
    Cria um novo curso.

    Expected JSON:
        {
            "nome": "Nome do curso",
            "descricao": "Descrição opcional",
            "materias": ["Matéria 1", "Matéria 2", ...]  # Lista de nomes das matérias
        }

    Returns:
        JSON: Dados do curso criado com suas matérias
    """
    try:
        dados = request.get_json()

        if not dados or "nome" not in dados:
            return jsonify({
                "success": False,
                "message": "Nome do curso é obrigatório"
            }), 400

        # Criar o curso
        novo_curso = Curso(nome=dados["nome"],
                           descricao=dados.get("descricao", ""))

        db.session.add(novo_curso)
        db.session.flush()  # Para obter o ID do curso antes do commit

        # Criar as matérias se fornecidas
        materias_criadas = []
        if "materias" in dados and isinstance(dados["materias"], list):
            for i, nome_materia in enumerate(dados["materias"]):
                if nome_materia.strip():  # Só cria se o nome não estiver vazio
                    nova_materia = Materia(nome=nome_materia.strip(),
                                           curso_id=novo_curso.id,
                                           ordem=i + 1)
                    db.session.add(nova_materia)
                    materias_criadas.append(nova_materia)

        db.session.commit()

        # Preparar resposta com o curso e suas matérias
        curso_dict = novo_curso.to_dict()
        curso_dict["materias"] = [
            materia.to_dict() for materia in materias_criadas
        ]

        return jsonify({
            "success": True,
            "message": "Curso criado com sucesso",
            "curso": curso_dict
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao criar curso: {str(e)}"
        }), 500


@cursos_bp.route("/cursos/<int:curso_id>", methods=["GET"])
def obter_curso(curso_id):
    """
    Obtém um curso específico com suas matérias.

    Args:
        curso_id (int): ID do curso

    Returns:
        JSON: Dados completos do curso com suas matérias
    """
    try:
        curso = Curso.query.get_or_404(curso_id)

        if not curso.ativo:
            return jsonify({
                "success": False,
                "message": "Curso não encontrado"
            }), 404

        # Obter matérias ordenadas
        materias = Materia.query.filter_by(curso_id=curso_id,
                                           ativo=True).order_by(
                                               Materia.ordem,
                                               Materia.nome).all()

        curso_dict = curso.to_dict()
        curso_dict["materias"] = [materia.to_dict() for materia in materias]

        return jsonify({"success": True, "curso": curso_dict}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao obter curso: {str(e)}"
        }), 500


@cursos_bp.route("/cursos/<int:curso_id>", methods=["PUT"])
def atualizar_curso(curso_id):
    """
    Atualiza um curso existente.

    Args:
        curso_id (int): ID do curso

    Expected JSON:
        {
            "nome": "Novo nome",
            "descricao": "Nova descrição",
            "materias": ["Nova Matéria 1", "Nova Matéria 2", ...] # Opcional: para atualizar matérias
        }

    Returns:
        JSON: Dados atualizados do curso
    """
    try:
        curso = Curso.query.get_or_404(curso_id)
        dados = request.get_json()

        if not dados:
            return jsonify({
                "success": False,
                "message": "Dados não fornecidos"
            }), 400

        # Atualizar campos se fornecidos
        if "nome" in dados:
            curso.nome = dados["nome"]
        if "descricao" in dados:
            curso.descricao = dados["descricao"]

        # Atualizar matérias
        if "materias" in dados and isinstance(dados["materias"], list):
            # Deletar matérias antigas que não estão na nova lista
            materias_atuais = {
                m.nome: m
                for m in Materia.query.filter_by(curso_id=curso_id).all()
            }
            nomes_materias_novas = [
                m.strip() for m in dados["materias"] if m.strip()
            ]

            for nome_atual, materia_obj in materias_atuais.items():
                if nome_atual not in nomes_materias_novas:
                    db.session.delete(materia_obj)

            # Adicionar ou atualizar matérias
            for i, nome_materia in enumerate(nomes_materias_novas):
                materia = Materia.query.filter_by(curso_id=curso_id,
                                                  nome=nome_materia).first()
                if materia:
                    materia.ordem = i + 1
                else:
                    nova_materia = Materia(nome=nome_materia,
                                           curso_id=curso_id,
                                           ordem=i + 1)
                    db.session.add(nova_materia)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Curso atualizado com sucesso",
            "curso": curso.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar curso: {str(e)}"
        }), 500


@cursos_bp.route("/cursos/<int:curso_id>", methods=["DELETE"])
def deletar_curso(curso_id):
    """
    Deleta um curso (soft delete - marca como inativo).

    Args:
        curso_id (int): ID do curso

    Returns:
        JSON: Confirmação da deleção
    """
    try:
        curso = Curso.query.get_or_404(curso_id)

        # Soft delete - marca como inativo
        curso.ativo = False

        # Também marca todas as matérias como inativas
        Materia.query.filter_by(curso_id=curso_id).update({"ativo": False})

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Curso deletado com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao deletar curso: {str(e)}"
        }), 500


# ===== ROTAS PARA MATÉRIAS =====


@cursos_bp.route("/materias/<int:materia_id>", methods=["GET"])
def obter_materia(materia_id):
    """
    Obtém uma matéria específica.

    Args:
        materia_id (int): ID da matéria

    Returns:
        JSON: Dados completos da matéria
    """
    try:
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                "success": False,
                "message": "Matéria não encontrada"
            }), 404

        return jsonify({"success": True, "materia": materia.to_dict()}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao obter matéria: {str(e)}"
        }), 500


@cursos_bp.route("/cursos/<int:curso_id>/materias", methods=["GET"])
def listar_materias(curso_id):
    """
    Lista todas as matérias de um curso.

    Args:
        curso_id (int): ID do curso

    Returns:
        JSON: Lista de matérias do curso
    """
    try:
        # Verificar se o curso existe
        curso = Curso.query.get_or_404(curso_id)

        if not curso.ativo:
            return jsonify({
                "success": False,
                "message": "Curso não encontrado"
            }), 404

        materias = Materia.query.filter_by(curso_id=curso_id,
                                           ativo=True).order_by(
                                               Materia.ordem,
                                               Materia.nome).all()

        return jsonify({
            "success": True,
            "materias": [materia.to_dict() for materia in materias]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erro ao listar matérias: {str(e)}"
        }), 500


@cursos_bp.route("/cursos/<int:curso_id>/materias", methods=["POST"])
def criar_materia(curso_id):
    """
    Cria uma nova matéria em um curso.

    Args:
        curso_id (int): ID do curso

    Expected JSON:
        {
            "nome": "Nome da matéria",
            "descricao": "Descrição opcional"
        }

    Returns:
        JSON: Dados da matéria criada
    """
    try:
        # Verificar se o curso existe
        curso = Curso.query.get_or_404(curso_id)

        if not curso.ativo:
            return jsonify({
                "success": False,
                "message": "Curso não encontrado"
            }), 404

        dados = request.get_json()

        if not dados or "nome" not in dados:
            return jsonify({
                "success": False,
                "message": "Nome da matéria é obrigatório"
            }), 400

        # Obter a próxima ordem
        ultima_ordem = db.session.query(db.func.max(
            Materia.ordem)).filter_by(curso_id=curso_id).scalar() or 0

        nova_materia = Materia(nome=dados["nome"],
                               descricao=dados.get("descricao", ""),
                               curso_id=curso_id,
                               ordem=ultima_ordem + 1)

        db.session.add(nova_materia)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Matéria criada com sucesso",
            "materia": nova_materia.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao criar matéria: {str(e)}"
        }), 500


@cursos_bp.route("/materias/<int:materia_id>", methods=["PUT"])
def atualizar_materia(materia_id):
    """
    Atualiza uma matéria existente.

    Args:
        materia_id (int): ID da matéria

    Expected JSON:
        {
            "nome": "Novo nome",
            "descricao": "Nova descrição"
        }

    Returns:
        JSON: Dados atualizados da matéria
    """
    try:
        materia = Materia.query.get_or_404(materia_id)
        dados = request.get_json()

        if not dados:
            return jsonify({
                "success": False,
                "message": "Dados não fornecidos"
            }), 400

        # Atualizar campos se fornecidos
        if "nome" in dados:
            materia.nome = dados["nome"]
        if "descricao" in dados:
            materia.descricao = dados["descricao"]

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Matéria atualizada com sucesso",
            "materia": materia.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao atualizar matéria: {str(e)}"
        }), 500


@cursos_bp.route("/materias/<int:materia_id>", methods=["DELETE"])
def deletar_materia(materia_id):
    """
    Deleta uma matéria (soft delete - marca como inativa).

    Args:
        materia_id (int): ID da matéria

    Returns:
        JSON: Confirmação da deleção
    """
    try:
        materia = Materia.query.get_or_404(materia_id)

        # Soft delete - marca como inativa
        materia.ativo = False

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Matéria deletada com sucesso"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erro ao deletar matéria: {str(e)}"
        }), 500
