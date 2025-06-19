from flask import Blueprint, request, jsonify
from src.models.user import User, db
from datetime import datetime

user_bp = Blueprint('user', __name__)


@user_bp.route('/user', methods=['GET'])
def listar_user():
    """
    Lista todos os cursos ativos.

    Returns:
        JSON: Lista de cursos com suas informações básicas
    """
    try:
        usuarios = User.query.filter_by(ativo=True).order_by(
            User.data_criacao.desc()).all()
        return jsonify({
            'success': True,
            'user': [user.to_dict() for user in user]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar usuarios: {str(e)}'
        }), 500


@user_bp.route('/user', methods=['POST'])
def criar_user():
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
    pass

      
@user_bp.route('/user/<int:user_id>', methods=['GET'])
def obter_user(curso_id):
    """
    Obtém um curso específico com suas matérias.

    Args:
        curso_id (int): ID do curso

    Returns:
        JSON: Dados completos do curso com suas matérias
    """
    try:
        user = User.query.get_or_404(user_id)

        if not user.ativo:
            return jsonify({
                'success': False,
                'message': 'User não encontrado'
            }), 404