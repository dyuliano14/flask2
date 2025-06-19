"""
Modelos de dados para o sistema de gerenciamento de estudos.

Este módulo contém todas as classes de modelo que representam as entidades
do sistema de estudos para concursos públicos, incluindo cursos, matérias,
conteúdos, flashcards e simulações.
"""

from datetime import datetime
from src.models.user import db


class Curso(db.Model):
    """
    Modelo para representar um curso/concurso.

    Um curso é o nível mais alto da hierarquia e pode conter várias matérias.
    Exemplo: "Concurso Alego 2024"
    """
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento com matérias
    materias = db.relationship('Materia',
                               backref='curso',
                               lazy=True,
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Curso {self.nome}>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id':
            self.id,
            'nome':
            self.nome,
            'descricao':
            self.descricao,
            'data_criacao':
            self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo':
            self.ativo,
            'total_materias':
            len(self.materias)
        }


class Materia(db.Model):
    """
    Modelo para representar uma matéria dentro de um curso.

    Uma matéria pertence a um curso e pode conter vários conteúdos.
    Exemplo: "Direito Constitucional", "Português", "Matemática"
    """
    __tablename__ = 'materias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, default=0)  # Para ordenação das matérias
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Chave estrangeira para o curso
    curso_id = db.Column(db.Integer,
                         db.ForeignKey('cursos.id'),
                         nullable=False)

    # Relacionamentos
    conteudos = db.relationship('Conteudo',
                                backref='materia',
                                lazy=True,
                                cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard',
                                 backref='materia',
                                 lazy=True,
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Materia {self.nome}>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id':
            self.id,
            'nome':
            self.nome,
            'descricao':
            self.descricao,
            'ordem':
            self.ordem,
            'data_criacao':
            self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo':
            self.ativo,
            'curso_id':
            self.curso_id,
            'total_conteudos':
            len(self.conteudos),
            'total_flashcards':
            len(self.flashcards)
        }


class Conteudo(db.Model):
    """
    Modelo para representar um conteúdo de estudo.

    Um conteúdo pode ser um PDF, um resumo em markdown ou um vídeo.
    Cada conteúdo pertence a uma matéria específica.
    """
    __tablename__ = 'conteudos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    tipo = db.Column(db.String(50),
                     nullable=False)  # 'pdf', 'markdown', 'video'
    arquivo_path = db.Column(db.String(500))  # Caminho para o arquivo
    conteudo_texto = db.Column(db.Text)  # Para conteúdo markdown ou texto
    ordem = db.Column(db.Integer, default=0)  # Para ordenação dos conteúdos
    estudado = db.Column(db.Boolean, default=False)  # Marca se já foi estudado
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_estudo = db.Column(db.DateTime)  # Quando foi estudado pela última vez

    # Chave estrangeira para a matéria
    materia_id = db.Column(db.Integer,
                           db.ForeignKey('materias.id'),
                           nullable=False)

    def __repr__(self):
        return f'<Conteudo {self.titulo}>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id':
            self.id,
            'titulo':
            self.titulo,
            'tipo':
            self.tipo,
            'arquivo_path':
            self.arquivo_path,
            'conteudo_texto':
            self.conteudo_texto,
            'ordem':
            self.ordem,
            'estudado':
            self.estudado,
            'data_criacao':
            self.data_criacao.isoformat() if self.data_criacao else None,
            'data_estudo':
            self.data_estudo.isoformat() if self.data_estudo else None,
            'materia_id':
            self.materia_id
        }


class Flashcard(db.Model):
    """
    Modelo para representar um flashcard de estudo.

    Cada flashcard tem uma pergunta (frente) e uma resposta (verso),
    além de metadados para controle de revisão espaçada.
    """
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    pergunta = db.Column(db.Text, nullable=False)
    resposta = db.Column(db.Text, nullable=False)
    dificuldade = db.Column(db.Integer,
                            default=1)  # 1=fácil, 2=médio, 3=difícil
    acertos = db.Column(db.Integer, default=0)
    erros = db.Column(db.Integer, default=0)
    ultima_revisao = db.Column(db.DateTime)
    proxima_revisao = db.Column(db.DateTime)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Chave estrangeira para a matéria
    materia_id = db.Column(db.Integer,
                           db.ForeignKey('materias.id'),
                           nullable=False)

    def __repr__(self):
        return f'<Flashcard {self.pergunta[:50]}...>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id':
            self.id,
            'pergunta':
            self.pergunta,
            'resposta':
            self.resposta,
            'dificuldade':
            self.dificuldade,
            'acertos':
            self.acertos,
            'erros':
            self.erros,
            'ultima_revisao':
            self.ultima_revisao.isoformat() if self.ultima_revisao else None,
            'proxima_revisao':
            self.proxima_revisao.isoformat() if self.proxima_revisao else None,
            'data_criacao':
            self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo':
            self.ativo,
            'materia_id':
            self.materia_id
        }


class Simulacao(db.Model):
    """
    Modelo para representar uma simulação de prova.

    Armazena informações sobre simulações realizadas, incluindo
    questões, respostas e desempenho.
    """
    __tablename__ = 'simulacoes'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    descricao = db.Column(db.Text)
    total_questoes = db.Column(db.Integer, default=0)
    acertos = db.Column(db.Integer, default=0)
    tempo_gasto = db.Column(db.Integer)  # Em minutos
    data_realizacao = db.Column(db.DateTime, default=datetime.utcnow)
    finalizada = db.Column(db.Boolean, default=False)

    # Chave estrangeira para o curso (simulações são por curso, não por matéria)
    curso_id = db.Column(db.Integer,
                         db.ForeignKey('cursos.id'),
                         nullable=False)

    # Relacionamento com questões
    questoes = db.relationship('QuestaoSimulacao',
                               backref='simulacao',
                               lazy=True,
                               cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Simulacao {self.titulo}>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        percentual = (self.acertos / self.total_questoes *
                      100) if self.total_questoes > 0 else 0
        return {
            'id':
            self.id,
            'titulo':
            self.titulo,
            'descricao':
            self.descricao,
            'total_questoes':
            self.total_questoes,
            'acertos':
            self.acertos,
            'tempo_gasto':
            self.tempo_gasto,
            'data_realizacao':
            self.data_realizacao.isoformat() if self.data_realizacao else None,
            'finalizada':
            self.finalizada,
            'curso_id':
            self.curso_id,
            'percentual_acerto':
            round(percentual, 2)
        }


class QuestaoSimulacao(db.Model):
    """
    Modelo para representar uma questão dentro de uma simulação.

    Cada questão tem um enunciado, alternativas e a resposta correta.
    """
    __tablename__ = 'questoes_simulacao'

    id = db.Column(db.Integer, primary_key=True)
    enunciado = db.Column(db.Text, nullable=False)
    alternativa_a = db.Column(db.Text)
    alternativa_b = db.Column(db.Text)
    alternativa_c = db.Column(db.Text)
    alternativa_d = db.Column(db.Text)
    alternativa_e = db.Column(db.Text)
    resposta_correta = db.Column(db.String(1),
                                 nullable=False)  # A, B, C, D ou E
    resposta_usuario = db.Column(db.String(1))  # Resposta dada pelo usuário
    acertou = db.Column(db.Boolean)
    ordem = db.Column(db.Integer, default=0)

    # Chave estrangeira para a simulação
    simulacao_id = db.Column(db.Integer,
                             db.ForeignKey('simulacoes.id'),
                             nullable=False)

    def __repr__(self):
        return f'<QuestaoSimulacao {self.enunciado[:50]}...>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id': self.id,
            'enunciado': self.enunciado,
            'alternativa_a': self.alternativa_a,
            'alternativa_b': self.alternativa_b,
            'alternativa_c': self.alternativa_c,
            'alternativa_d': self.alternativa_d,
            'alternativa_e': self.alternativa_e,
            'resposta_correta': self.resposta_correta,
            'resposta_usuario': self.resposta_usuario,
            'acertou': self.acertou,
            'ordem': self.ordem,
            'simulacao_id': self.simulacao_id
        }


class RegistroFeynman(db.Model):
    """
    Modelo para armazenar registros da técnica Feynman.

    Permite ao usuário salvar suas explicações e acompanhar
    o progresso na compreensão dos tópicos.
    """
    __tablename__ = 'registros_feynman'

    id = db.Column(db.Integer, primary_key=True)
    topico = db.Column(db.String(300), nullable=False)
    explicacao = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)

    # Chave estrangeira para a matéria
    materia_id = db.Column(db.Integer,
                           db.ForeignKey('materias.id'),
                           nullable=False)

    def __repr__(self):
        return f'<RegistroFeynman {self.topico}>'

    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON."""
        return {
            'id':
            self.id,
            'topico':
            self.topico,
            'explicacao':
            self.explicacao,
            'data_criacao':
            self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao':
            self.data_atualizacao.isoformat()
            if self.data_atualizacao else None,
            'materia_id':
            self.materia_id
        }
