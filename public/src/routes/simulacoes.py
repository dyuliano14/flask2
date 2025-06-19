"""
Rotas para simulações de prova e técnica Feynman.

Este módulo contém todas as rotas relacionadas às simulações de prova
e aos registros da técnica Feynman do sistema de estudos.
"""

from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.estudo import Simulacao, QuestaoSimulacao, RegistroFeynman, Curso, Materia
from datetime import datetime

# Criação do blueprint para as rotas de simulações e Feynman
simulacoes_bp = Blueprint('simulacoes', __name__)

# ===== ROTAS PARA SIMULAÇÕES =====


@simulacoes_bp.route('/cursos/<int:curso_id>/simulacoes', methods=['GET'])
def listar_simulacoes(curso_id):
    """
    Lista todas as simulações de um curso.

    Args:
        curso_id (int): ID do curso

    Returns:
        JSON: Lista de simulações do curso
    """
    try:
        # Verificar se o curso existe
        curso = Curso.query.get_or_404(curso_id)

        if not curso.ativo:
            return jsonify({
                'success': False,
                'message': 'Curso não encontrado'
            }), 404

        simulacoes = Simulacao.query.filter_by(curso_id=curso_id).order_by(
            Simulacao.data_realizacao.desc()).all()

        return jsonify({
            'success':
            True,
            'simulacoes': [simulacao.to_dict() for simulacao in simulacoes]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar simulações: {str(e)}'
        }), 500


@simulacoes_bp.route('/cursos/<int:curso_id>/simulacoes', methods=['POST'])
def criar_simulacao(curso_id):
    """
    Cria uma nova simulação de prova.

    Args:
        curso_id (int): ID do curso

    Expected JSON:
        {
            "titulo": "Simulado Alego 2024",
            "descricao": "Descrição opcional",
            "questoes": [
                {
                    "enunciado": "Pergunta 1...",
                    "alternativa_a": "Opção A",
                    "alternativa_b": "Opção B",
                    "alternativa_c": "Opção C",
                    "alternativa_d": "Opção D",
                    "alternativa_e": "Opção E",
                    "resposta_correta": "A"
                },
                ...
            ]
        }

    Returns:
        JSON: Dados da simulação criada
    """
    try:
        # Verificar se o curso existe
        curso = Curso.query.get_or_404(curso_id)

        if not curso.ativo:
            return jsonify({
                'success': False,
                'message': 'Curso não encontrado'
            }), 404

        dados = request.get_json()

        if not dados or 'titulo' not in dados:
            return jsonify({
                'success': False,
                'message': 'Título é obrigatório'
            }), 400

        questoes_data = dados.get('questoes', [])

        if not questoes_data:
            return jsonify({
                'success': False,
                'message': 'Pelo menos uma questão é obrigatória'
            }), 400

        # Criar a simulação
        nova_simulacao = Simulacao(titulo=dados['titulo'],
                                   descricao=dados.get('descricao', ''),
                                   total_questoes=len(questoes_data),
                                   curso_id=curso_id)

        db.session.add(nova_simulacao)
        db.session.flush()  # Para obter o ID da simulação

        # Criar as questões
        questoes_criadas = []
        for i, questao_data in enumerate(questoes_data):
            if not all(key in questao_data
                       for key in ['enunciado', 'resposta_correta']):
                db.session.rollback()
                return jsonify({
                    'success':
                    False,
                    'message':
                    f'Questão {i+1}: enunciado e resposta_correta são obrigatórios'
                }), 400

            nova_questao = QuestaoSimulacao(
                enunciado=questao_data['enunciado'],
                alternativa_a=questao_data.get('alternativa_a', ''),
                alternativa_b=questao_data.get('alternativa_b', ''),
                alternativa_c=questao_data.get('alternativa_c', ''),
                alternativa_d=questao_data.get('alternativa_d', ''),
                alternativa_e=questao_data.get('alternativa_e', ''),
                resposta_correta=questao_data['resposta_correta'].upper(),
                ordem=i + 1,
                simulacao_id=nova_simulacao.id)

            db.session.add(nova_questao)
            questoes_criadas.append(nova_questao)

        db.session.commit()

        # Preparar resposta
        simulacao_dict = nova_simulacao.to_dict()
        simulacao_dict['questoes'] = [
            questao.to_dict() for questao in questoes_criadas
        ]

        return jsonify({
            'success': True,
            'message': 'Simulação criada com sucesso',
            'simulacao': simulacao_dict
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar simulação: {str(e)}'
        }), 500


@simulacoes_bp.route('/simulacoes/<int:simulacao_id>', methods=['GET'])
def obter_simulacao(simulacao_id):
    """
    Obtém uma simulação específica com suas questões.

    Args:
        simulacao_id (int): ID da simulação

    Returns:
        JSON: Dados completos da simulação
    """
    try:
        simulacao = Simulacao.query.get_or_404(simulacao_id)

        # Obter questões ordenadas
        questoes = QuestaoSimulacao.query.filter_by(
            simulacao_id=simulacao_id).order_by(QuestaoSimulacao.ordem).all()

        simulacao_dict = simulacao.to_dict()
        simulacao_dict['questoes'] = [
            questao.to_dict() for questao in questoes
        ]

        return jsonify({'success': True, 'simulacao': simulacao_dict}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter simulação: {str(e)}'
        }), 500


@simulacoes_bp.route('/simulacoes/<int:simulacao_id>/responder',
                     methods=['PUT'])
def responder_simulacao(simulacao_id):
    """
    Registra as respostas de uma simulação e calcula o resultado.

    Args:
        simulacao_id (int): ID da simulação

    Expected JSON:
        {
            "respostas": {
                "1": "A",  # questao_id: resposta
                "2": "B",
                ...
            },
            "tempo_gasto": 120  # em minutos (opcional)
        }

    Returns:
        JSON: Resultado da simulação
    """
    try:
        simulacao = Simulacao.query.get_or_404(simulacao_id)
        dados = request.get_json()

        if not dados or 'respostas' not in dados:
            return jsonify({
                'success': False,
                'message': 'Respostas são obrigatórias'
            }), 400

        respostas = dados['respostas']
        tempo_gasto = dados.get('tempo_gasto')

        # Obter todas as questões da simulação
        questoes = QuestaoSimulacao.query.filter_by(
            simulacao_id=simulacao_id).all()

        acertos = 0

        # Processar cada questão
        for questao in questoes:
            resposta_usuario = respostas.get(str(questao.id), '').upper()
            questao.resposta_usuario = resposta_usuario

            if resposta_usuario == questao.resposta_correta:
                questao.acertou = True
                acertos += 1
            else:
                questao.acertou = False

        # Atualizar a simulação
        simulacao.acertos = acertos
        simulacao.finalizada = True
        if tempo_gasto:
            simulacao.tempo_gasto = tempo_gasto

        db.session.commit()

        # Preparar resultado
        resultado = simulacao.to_dict()
        resultado['questoes'] = [questao.to_dict() for questao in questoes]

        return jsonify({
            'success': True,
            'message': 'Simulação finalizada com sucesso',
            'resultado': resultado
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao processar respostas: {str(e)}'
        }), 500


@simulacoes_bp.route('/simulacoes/<int:simulacao_id>/estatisticas',
                     methods=['GET'])
def estatisticas_simulacao(simulacao_id):
    """
    Obtém estatísticas detalhadas de uma simulação.

    Args:
        simulacao_id (int): ID da simulação

    Returns:
        JSON: Estatísticas da simulação
    """
    try:
        simulacao = Simulacao.query.get_or_404(simulacao_id)

        if not simulacao.finalizada:
            return jsonify({
                'success': False,
                'message': 'Simulação ainda não foi finalizada'
            }), 400

        questoes = QuestaoSimulacao.query.filter_by(
            simulacao_id=simulacao_id).all()

        # Calcular estatísticas
        total_questoes = len(questoes)
        acertos = sum(1 for q in questoes if q.acertou)
        erros = total_questoes - acertos
        percentual = (acertos / total_questoes *
                      100) if total_questoes > 0 else 0

        # Estatísticas por alternativa
        distribuicao_respostas = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        for questao in questoes:
            if questao.resposta_usuario in distribuicao_respostas:
                distribuicao_respostas[questao.resposta_usuario] += 1

        estatisticas = {
            'total_questoes':
            total_questoes,
            'acertos':
            acertos,
            'erros':
            erros,
            'percentual_acerto':
            round(percentual, 2),
            'tempo_gasto':
            simulacao.tempo_gasto,
            'distribuicao_respostas':
            distribuicao_respostas,
            'questoes_detalhadas': [{
                'questao_id': q.id,
                'ordem': q.ordem,
                'resposta_correta': q.resposta_correta,
                'resposta_usuario': q.resposta_usuario,
                'acertou': q.acertou
            } for q in questoes]
        }

        return jsonify({'success': True, 'estatisticas': estatisticas}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter estatísticas: {str(e)}'
        }), 500


# ===== ROTAS PARA TÉCNICA FEYNMAN =====


@simulacoes_bp.route('/materias/<int:materia_id>/feynman', methods=['GET'])
def listar_registros_feynman(materia_id):
    """
    Lista todos os registros Feynman de uma matéria.

    Args:
        materia_id (int): ID da matéria

    Returns:
        JSON: Lista de registros Feynman da matéria
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                'success': False,
                'message': 'Matéria não encontrada'
            }), 404

        registros = RegistroFeynman.query.filter_by(
            materia_id=materia_id).order_by(
                RegistroFeynman.data_atualizacao.desc()).all()

        return jsonify({
            'success':
            True,
            'registros': [registro.to_dict() for registro in registros]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar registros Feynman: {str(e)}'
        }), 500


@simulacoes_bp.route('/materias/<int:materia_id>/feynman', methods=['POST'])
def criar_registro_feynman(materia_id):
    """
    Cria um novo registro da técnica Feynman.

    Args:
        materia_id (int): ID da matéria

    Expected JSON:
        {
            "topico": "Tópico explicado",
            "explicacao": "Explicação detalhada usando a técnica Feynman..."
        }

    Returns:
        JSON: Dados do registro criado
    """
    try:
        # Verificar se a matéria existe
        materia = Materia.query.get_or_404(materia_id)

        if not materia.ativo:
            return jsonify({
                'success': False,
                'message': 'Matéria não encontrada'
            }), 404

        dados = request.get_json()

        if not dados or 'topico' not in dados or 'explicacao' not in dados:
            return jsonify({
                'success': False,
                'message': 'Tópico e explicação são obrigatórios'
            }), 400

        novo_registro = RegistroFeynman(topico=dados['topico'],
                                        explicacao=dados['explicacao'],
                                        materia_id=materia_id)

        db.session.add(novo_registro)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registro Feynman criado com sucesso',
            'registro': novo_registro.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar registro Feynman: {str(e)}'
        }), 500


@simulacoes_bp.route('/feynman/<int:registro_id>', methods=['GET'])
def obter_registro_feynman(registro_id):
    """
    Obtém um registro Feynman específico.

    Args:
        registro_id (int): ID do registro

    Returns:
        JSON: Dados completos do registro
    """
    try:
        registro = RegistroFeynman.query.get_or_404(registro_id)

        return jsonify({'success': True, 'registro': registro.to_dict()}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter registro Feynman: {str(e)}'
        }), 500


@simulacoes_bp.route('/feynman/<int:registro_id>', methods=['PUT'])
def atualizar_registro_feynman(registro_id):
    """
    Atualiza um registro Feynman existente.

    Args:
        registro_id (int): ID do registro

    Expected JSON:
        {
            "topico": "Novo tópico",
            "explicacao": "Nova explicação..."
        }

    Returns:
        JSON: Dados atualizados do registro
    """
    try:
        registro = RegistroFeynman.query.get_or_404(registro_id)
        dados = request.get_json()

        if not dados:
            return jsonify({
                'success': False,
                'message': 'Dados não fornecidos'
            }), 400

        # Atualizar campos se fornecidos
        if 'topico' in dados:
            registro.topico = dados['topico']
        if 'explicacao' in dados:
            registro.explicacao = dados['explicacao']

        registro.data_atualizacao = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registro Feynman atualizado com sucesso',
            'registro': registro.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success':
            False,
            'message':
            f'Erro ao atualizar registro Feynman: {str(e)}'
        }), 500


@simulacoes_bp.route('/feynman/<int:registro_id>', methods=['DELETE'])
def deletar_registro_feynman(registro_id):
    """
    Deleta um registro Feynman.

    Args:
        registro_id (int): ID do registro

    Returns:
        JSON: Confirmação da deleção
    """
    try:
        registro = RegistroFeynman.query.get_or_404(registro_id)

        db.session.delete(registro)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Registro Feynman deletado com sucesso'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar registro Feynman: {str(e)}'
        }), 500
