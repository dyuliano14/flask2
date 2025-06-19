"""
Testes unitários para o sistema de gerenciamento de estudos.

Este módulo contém testes abrangentes para todas as funcionalidades
da API Flask, incluindo CRUD de cursos, matérias, conteúdos, flashcards,
simulações e registros Feynman.

Para executar os testes:
    pytest tests/

Para executar com cobertura:
    pytest --cov=src tests/
"""

import pytest
import json
import os
import tempfile
from src.main import app
from src.models.user import db
from src.models.estudo import Curso, Materia, Conteudo, Flashcard, Simulacao, QuestaoSimulacao, RegistroFeynman


@pytest.fixture
def client():
    """
    Fixture que cria um cliente de teste para a aplicação Flask.

    Configura um banco de dados temporário em memória para os testes,
    garantindo que os testes não afetem o banco de dados principal.
    """
    # Configurar banco de dados de teste em memória
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            # Criar todas as tabelas
            db.create_all()
            yield client
            # Limpar após os testes
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_curso(client):
    """
    Fixture que cria um curso de exemplo para os testes.

    Returns:
        dict: Dados do curso criado
    """
    curso_data = {
        'nome': 'Concurso Alego 2024',
        'descricao':
        'Preparação para o concurso da Assembleia Legislativa de Goiás',
        'materias': ['Direito Constitucional', 'Português', 'Matemática']
    }

    response = client.post('/api/cursos',
                           data=json.dumps(curso_data),
                           content_type='application/json')

    assert response.status_code == 201
    return response.get_json()['curso']


@pytest.fixture
def sample_materia(client, sample_curso):
    """
    Fixture que cria uma matéria de exemplo para os testes.

    Args:
        sample_curso: Curso criado pela fixture sample_curso

    Returns:
        dict: Dados da matéria criada
    """
    # Pegar a primeira matéria do curso
    return sample_curso['materias'][0]


class TestCursos:
    """Testes para as operações CRUD de cursos."""

    def test_listar_cursos_vazio(self, client):
        """Testa a listagem quando não há cursos cadastrados."""
        response = client.get('/api/cursos')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['cursos'] == []

    def test_criar_curso_sucesso(self, client):
        """Testa a criação bem-sucedida de um curso."""
        curso_data = {
            'nome': 'Concurso Teste',
            'descricao': 'Descrição do curso de teste',
            'materias': ['Matéria 1', 'Matéria 2']
        }

        response = client.post('/api/cursos',
                               data=json.dumps(curso_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['curso']['nome'] == curso_data['nome']
        assert data['curso']['descricao'] == curso_data['descricao']
        assert len(data['curso']['materias']) == 2

    def test_criar_curso_sem_nome(self, client):
        """Testa a criação de curso sem nome (deve falhar)."""
        curso_data = {'descricao': 'Descrição sem nome'}

        response = client.post('/api/cursos',
                               data=json.dumps(curso_data),
                               content_type='application/json')

        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False
        assert 'obrigatório' in data['message'].lower()

    def test_obter_curso_existente(self, client, sample_curso):
        """Testa a obtenção de um curso existente."""
        curso_id = sample_curso['id']

        response = client.get(f'/api/cursos/{curso_id}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['curso']['id'] == curso_id
        assert data['curso']['nome'] == sample_curso['nome']

    def test_obter_curso_inexistente(self, client):
        """Testa a obtenção de um curso que não existe."""
        response = client.get('/api/cursos/999')
        assert response.status_code == 404

    def test_atualizar_curso(self, client, sample_curso):
        """Testa a atualização de um curso existente."""
        curso_id = sample_curso['id']
        update_data = {
            'nome': 'Nome Atualizado',
            'descricao': 'Descrição Atualizada'
        }

        response = client.put(f'/api/cursos/{curso_id}',
                              data=json.dumps(update_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['curso']['nome'] == update_data['nome']
        assert data['curso']['descricao'] == update_data['descricao']

    def test_deletar_curso(self, client, sample_curso):
        """Testa a deleção (soft delete) de um curso."""
        curso_id = sample_curso['id']

        response = client.delete(f'/api/cursos/{curso_id}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True

        # Verificar que o curso não aparece mais na listagem
        response = client.get('/api/cursos')
        data = response.get_json()
        assert len(data['cursos']) == 0


class TestMaterias:
    """Testes para as operações CRUD de matérias."""

    def test_listar_materias(self, client, sample_curso):
        """Testa a listagem de matérias de um curso."""
        curso_id = sample_curso['id']

        response = client.get(f'/api/cursos/{curso_id}/materias')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert len(data['materias']) == 3  # Criadas na fixture

    def test_criar_materia(self, client, sample_curso):
        """Testa a criação de uma nova matéria."""
        curso_id = sample_curso['id']
        materia_data = {
            'nome': 'Nova Matéria',
            'descricao': 'Descrição da nova matéria'
        }

        response = client.post(f'/api/cursos/{curso_id}/materias',
                               data=json.dumps(materia_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['materia']['nome'] == materia_data['nome']
        assert data['materia']['curso_id'] == curso_id

    def test_criar_materia_curso_inexistente(self, client):
        """Testa a criação de matéria em curso inexistente."""
        materia_data = {'nome': 'Matéria Teste'}

        response = client.post('/api/cursos/999/materias',
                               data=json.dumps(materia_data),
                               content_type='application/json')

        assert response.status_code == 404

    def test_atualizar_materia(self, client, sample_materia):
        """Testa a atualização de uma matéria."""
        materia_id = sample_materia['id']
        update_data = {
            'nome': 'Nome Atualizado',
            'descricao': 'Descrição Atualizada'
        }

        response = client.put(f'/api/materias/{materia_id}',
                              data=json.dumps(update_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['materia']['nome'] == update_data['nome']

    def test_deletar_materia(self, client, sample_materia):
        """Testa a deleção de uma matéria."""
        materia_id = sample_materia['id']

        response = client.delete(f'/api/materias/{materia_id}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True


class TestConteudos:
    """Testes para as operações CRUD de conteúdos."""

    def test_listar_conteudos_vazio(self, client, sample_materia):
        """Testa a listagem quando não há conteúdos."""
        materia_id = sample_materia['id']

        response = client.get(f'/api/materias/{materia_id}/conteudos')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['conteudos'] == []

    def test_criar_conteudo_markdown(self, client, sample_materia):
        """Testa a criação de conteúdo tipo markdown."""
        materia_id = sample_materia['id']
        conteudo_data = {
            'titulo': 'Resumo de Direito Constitucional',
            'tipo': 'markdown',
            'conteudo_texto':
            '# Princípios Fundamentais\n\nConteúdo do resumo...'
        }

        response = client.post(f'/api/materias/{materia_id}/conteudos',
                               data=json.dumps(conteudo_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['conteudo']['titulo'] == conteudo_data['titulo']
        assert data['conteudo']['tipo'] == 'markdown'
        assert data['conteudo']['materia_id'] == materia_id

    def test_criar_conteudo_sem_titulo(self, client, sample_materia):
        """Testa a criação de conteúdo sem título (deve falhar)."""
        materia_id = sample_materia['id']
        conteudo_data = {
            'tipo': 'markdown',
            'conteudo_texto': 'Conteúdo sem título'
        }

        response = client.post(f'/api/materias/{materia_id}/conteudos',
                               data=json.dumps(conteudo_data),
                               content_type='application/json')

        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False

    def test_marcar_conteudo_estudado(self, client, sample_materia):
        """Testa marcar um conteúdo como estudado."""
        # Primeiro criar um conteúdo
        materia_id = sample_materia['id']
        conteudo_data = {
            'titulo': 'Conteúdo para Estudar',
            'tipo': 'markdown',
            'conteudo_texto': 'Conteúdo de teste'
        }

        response = client.post(f'/api/materias/{materia_id}/conteudos',
                               data=json.dumps(conteudo_data),
                               content_type='application/json')

        conteudo_id = response.get_json()['conteudo']['id']

        # Marcar como estudado
        response = client.put(f'/api/conteudos/{conteudo_id}/marcar-estudado')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['conteudo']['estudado'] is True
        assert data['conteudo']['data_estudo'] is not None


class TestFlashcards:
    """Testes para as operações CRUD de flashcards."""

    def test_listar_flashcards_vazio(self, client, sample_materia):
        """Testa a listagem quando não há flashcards."""
        materia_id = sample_materia['id']

        response = client.get(f'/api/materias/{materia_id}/flashcards')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['flashcards'] == []

    def test_criar_flashcard(self, client, sample_materia):
        """Testa a criação de um flashcard."""
        materia_id = sample_materia['id']
        flashcard_data = {
            'pergunta': 'O que é a Constituição Federal?',
            'resposta': 'É a lei fundamental e suprema do Estado brasileiro.',
            'dificuldade': 2
        }

        response = client.post(f'/api/materias/{materia_id}/flashcards',
                               data=json.dumps(flashcard_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['flashcard']['pergunta'] == flashcard_data['pergunta']
        assert data['flashcard']['resposta'] == flashcard_data['resposta']
        assert data['flashcard']['dificuldade'] == flashcard_data[
            'dificuldade']
        assert data['flashcard']['materia_id'] == materia_id

    def test_criar_flashcard_sem_pergunta(self, client, sample_materia):
        """Testa a criação de flashcard sem pergunta (deve falhar)."""
        materia_id = sample_materia['id']
        flashcard_data = {'resposta': 'Resposta sem pergunta'}

        response = client.post(f'/api/materias/{materia_id}/flashcards',
                               data=json.dumps(flashcard_data),
                               content_type='application/json')

        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False

    def test_responder_flashcard_acerto(self, client, sample_materia):
        """Testa responder um flashcard corretamente."""
        # Primeiro criar um flashcard
        materia_id = sample_materia['id']
        flashcard_data = {
            'pergunta': 'Pergunta teste',
            'resposta': 'Resposta teste'
        }

        response = client.post(f'/api/materias/{materia_id}/flashcards',
                               data=json.dumps(flashcard_data),
                               content_type='application/json')

        flashcard_id = response.get_json()['flashcard']['id']

        # Responder corretamente
        resposta_data = {'acertou': True}

        response = client.put(f'/api/flashcards/{flashcard_id}/responder',
                              data=json.dumps(resposta_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['flashcard']['acertos'] == 1
        assert data['flashcard']['erros'] == 0
        assert data['flashcard']['ultima_revisao'] is not None

    def test_responder_flashcard_erro(self, client, sample_materia):
        """Testa responder um flashcard incorretamente."""
        # Primeiro criar um flashcard
        materia_id = sample_materia['id']
        flashcard_data = {
            'pergunta': 'Pergunta teste',
            'resposta': 'Resposta teste'
        }

        response = client.post(f'/api/materias/{materia_id}/flashcards',
                               data=json.dumps(flashcard_data),
                               content_type='application/json')

        flashcard_id = response.get_json()['flashcard']['id']

        # Responder incorretamente
        resposta_data = {'acertou': False}

        response = client.put(f'/api/flashcards/{flashcard_id}/responder',
                              data=json.dumps(resposta_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['flashcard']['acertos'] == 0
        assert data['flashcard']['erros'] == 1

    def test_flashcards_para_revisar(self, client):
        """Testa a obtenção de flashcards para revisar."""
        response = client.get('/api/flashcards/revisar')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert 'flashcards' in data
        assert 'total' in data


class TestSimulacoes:
    """Testes para as operações de simulações."""

    def test_listar_simulacoes_vazio(self, client, sample_curso):
        """Testa a listagem quando não há simulações."""
        curso_id = sample_curso['id']

        response = client.get(f'/api/cursos/{curso_id}/simulacoes')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['simulacoes'] == []

    def test_criar_simulacao(self, client, sample_curso):
        """Testa a criação de uma simulação."""
        curso_id = sample_curso['id']
        simulacao_data = {
            'titulo':
            'Simulado Alego 2024 - Prova 1',
            'descricao':
            'Primeira simulação do concurso',
            'questoes': [{
                'enunciado': 'Qual é a capital do Brasil?',
                'alternativa_a': 'São Paulo',
                'alternativa_b': 'Rio de Janeiro',
                'alternativa_c': 'Brasília',
                'alternativa_d': 'Belo Horizonte',
                'alternativa_e': 'Salvador',
                'resposta_correta': 'C'
            }, {
                'enunciado': 'Quantos estados tem o Brasil?',
                'alternativa_a': '25',
                'alternativa_b': '26',
                'alternativa_c': '27',
                'alternativa_d': '28',
                'alternativa_e': '29',
                'resposta_correta': 'C'
            }]
        }

        response = client.post(f'/api/cursos/{curso_id}/simulacoes',
                               data=json.dumps(simulacao_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['simulacao']['titulo'] == simulacao_data['titulo']
        assert data['simulacao']['total_questoes'] == 2
        assert len(data['simulacao']['questoes']) == 2

    def test_criar_simulacao_sem_questoes(self, client, sample_curso):
        """Testa a criação de simulação sem questões (deve falhar)."""
        curso_id = sample_curso['id']
        simulacao_data = {'titulo': 'Simulação sem questões', 'questoes': []}

        response = client.post(f'/api/cursos/{curso_id}/simulacoes',
                               data=json.dumps(simulacao_data),
                               content_type='application/json')

        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False

    def test_responder_simulacao(self, client, sample_curso):
        """Testa responder uma simulação completa."""
        # Primeiro criar uma simulação
        curso_id = sample_curso['id']
        simulacao_data = {
            'titulo':
            'Simulação Teste',
            'questoes': [{
                'enunciado': 'Questão 1',
                'alternativa_a': 'A',
                'alternativa_b': 'B',
                'alternativa_c': 'C',
                'resposta_correta': 'A'
            }, {
                'enunciado': 'Questão 2',
                'alternativa_a': 'A',
                'alternativa_b': 'B',
                'alternativa_c': 'C',
                'resposta_correta': 'B'
            }]
        }

        response = client.post(f'/api/cursos/{curso_id}/simulacoes',
                               data=json.dumps(simulacao_data),
                               content_type='application/json')

        simulacao = response.get_json()['simulacao']
        simulacao_id = simulacao['id']
        questoes = simulacao['questoes']

        # Responder a simulação
        respostas_data = {
            'respostas': {
                str(questoes[0]['id']): 'A',  # Correta
                str(questoes[1]['id']): 'C'  # Incorreta
            },
            'tempo_gasto': 30
        }

        response = client.put(f'/api/simulacoes/{simulacao_id}/responder',
                              data=json.dumps(respostas_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['resultado']['acertos'] == 1
        assert data['resultado']['finalizada'] is True
        assert data['resultado']['tempo_gasto'] == 30


class TestFeynman:
    """Testes para os registros da técnica Feynman."""

    def test_listar_registros_vazio(self, client, sample_materia):
        """Testa a listagem quando não há registros."""
        materia_id = sample_materia['id']

        response = client.get(f'/api/materias/{materia_id}/feynman')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['registros'] == []

    def test_criar_registro_feynman(self, client, sample_materia):
        """Testa a criação de um registro Feynman."""
        materia_id = sample_materia['id']
        registro_data = {
            'topico':
            'Princípios Constitucionais',
            'explicacao':
            'Os princípios constitucionais são normas fundamentais que orientam todo o ordenamento jurídico. Eles servem como base para a interpretação e aplicação das demais normas constitucionais e infraconstitucionais.'
        }

        response = client.post(f'/api/materias/{materia_id}/feynman',
                               data=json.dumps(registro_data),
                               content_type='application/json')

        assert response.status_code == 201

        data = response.get_json()
        assert data['success'] is True
        assert data['registro']['topico'] == registro_data['topico']
        assert data['registro']['explicacao'] == registro_data['explicacao']
        assert data['registro']['materia_id'] == materia_id

    def test_criar_registro_sem_topico(self, client, sample_materia):
        """Testa a criação de registro sem tópico (deve falhar)."""
        materia_id = sample_materia['id']
        registro_data = {'explicacao': 'Explicação sem tópico'}

        response = client.post(f'/api/materias/{materia_id}/feynman',
                               data=json.dumps(registro_data),
                               content_type='application/json')

        assert response.status_code == 400

        data = response.get_json()
        assert data['success'] is False

    def test_atualizar_registro_feynman(self, client, sample_materia):
        """Testa a atualização de um registro Feynman."""
        # Primeiro criar um registro
        materia_id = sample_materia['id']
        registro_data = {
            'topico': 'Tópico Original',
            'explicacao': 'Explicação original'
        }

        response = client.post(f'/api/materias/{materia_id}/feynman',
                               data=json.dumps(registro_data),
                               content_type='application/json')

        registro_id = response.get_json()['registro']['id']

        # Atualizar o registro
        update_data = {
            'topico': 'Tópico Atualizado',
            'explicacao': 'Explicação atualizada e melhorada'
        }

        response = client.put(f'/api/feynman/{registro_id}',
                              data=json.dumps(update_data),
                              content_type='application/json')

        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True
        assert data['registro']['topico'] == update_data['topico']
        assert data['registro']['explicacao'] == update_data['explicacao']

    def test_deletar_registro_feynman(self, client, sample_materia):
        """Testa a deleção de um registro Feynman."""
        # Primeiro criar um registro
        materia_id = sample_materia['id']
        registro_data = {
            'topico': 'Tópico para Deletar',
            'explicacao': 'Explicação para deletar'
        }

        response = client.post(f'/api/materias/{materia_id}/feynman',
                               data=json.dumps(registro_data),
                               content_type='application/json')

        registro_id = response.get_json()['registro']['id']

        # Deletar o registro
        response = client.delete(f'/api/feynman/{registro_id}')
        assert response.status_code == 200

        data = response.get_json()
        assert data['success'] is True

        # Verificar que foi deletado
        response = client.get(f'/api/feynman/{registro_id}')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__])
