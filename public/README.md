# Estudo Alego - Gerenciador de Estudos para Concursos Públicos

## Visão Geral

O **Estudo Alego** é um sistema completo de gerenciamento de estudos desenvolvido especificamente para preparação de concursos públicos, com foco no concurso da Assembleia Legislativa de Goiás (Alego). O sistema implementa metodologias ativas de aprendizagem, incluindo técnicas como Feynman, flashcards com repetição espaçada, simulações de prova e organização estruturada de conteúdos.

### Características Principais

- **Metodologias Ativas**: Implementação de técnicas comprovadas de aprendizagem
- **Organização Hierárquica**: Estrutura de cursos → matérias → conteúdos
- **Flashcards Inteligentes**: Sistema de repetição espaçada para memorização eficaz
- **Técnica Feynman**: Espaço dedicado para explicações e consolidação do aprendizado
- **Simulações de Prova**: Ambiente para prática com questões de concursos anteriores
- **Interface Moderna**: Design limpo e responsivo com foco na experiência do usuário
- **API RESTful**: Backend robusto com documentação completa

## Arquitetura do Sistema

### Backend (Flask)

O backend é construído com Flask e segue uma arquitetura modular:

```
src/
├── models/          # Modelos de dados (SQLAlchemy)
│   ├── user.py      # Configuração do banco de dados
│   └── estudo.py    # Modelos do sistema de estudos
├── routes/          # Rotas da API (Blueprints)
│   ├── user.py      # Rotas de usuário (template)
│   ├── cursos.py    # CRUD de cursos e matérias
│   ├── conteudos.py # CRUD de conteúdos e flashcards
│   └── simulacoes.py # Simulações e técnica Feynman
├── static/          # Frontend (HTML, CSS, JavaScript)
│   ├── index.html   # Interface principal
│   ├── styles.css   # Estilos da aplicação
│   └── app.js       # Lógica JavaScript
├── database/        # Banco de dados SQLite
└── main.py          # Ponto de entrada da aplicação
```

### Frontend (HTML/CSS/JavaScript)

O frontend é uma Single Page Application (SPA) que se comunica com a API via AJAX:

- **HTML5**: Estrutura semântica e acessível
- **CSS3**: Design responsivo com Flexbox e Grid
- **JavaScript ES6+**: Lógica de interação e comunicação com API
- **Font Awesome**: Ícones para melhor experiência visual

### Banco de Dados

Utiliza SQLite com SQLAlchemy ORM, com as seguintes entidades principais:

- **Curso**: Representa um concurso ou área de estudo
- **Materia**: Disciplinas dentro de um curso
- **Conteudo**: PDFs, resumos em markdown ou vídeos
- **Flashcard**: Cards para memorização com algoritmo de repetição
- **Simulacao**: Provas simuladas com questões
- **QuestaoSimulacao**: Questões individuais das simulações
- **RegistroFeynman**: Registros da técnica Feynman

## Metodologias de Aprendizagem Implementadas

### 1. Leitura Ativa e Resolução de Exercícios

O sistema permite organizar conteúdos em "partes coerentes", facilitando o estudo estruturado:

- Upload de PDFs divididos em seções lógicas
- Marcação de progresso (estudado/não estudado)
- Resumos em markdown para revisão rápida

### 2. Técnica Feynman

Espaço dedicado para o usuário explicar conceitos com suas próprias palavras:

- Criação de registros por tópico
- Edição e refinamento das explicações
- Organização por matéria para fácil localização

### 3. Flashcards com Repetição Espaçada

Sistema inteligente de memorização baseado no desempenho:

```python
# Algoritmo de repetição espaçada implementado
if acertou:
    if flashcard.acertos == 1:
        dias = 1
    elif flashcard.acertos == 2:
        dias = 3
    elif flashcard.acertos == 3:
        dias = 7
    else:
        dias = min(30, flashcard.acertos * 3)
else:
    dias = 1  # Volta para 1 dia se errou
    flashcard.acertos = 0  # Reset dos acertos
```

### 4. Simulação de Provas

Ambiente completo para prática:

- Criação de simulações com múltiplas questões
- Cronometragem de tempo
- Cálculo automático de desempenho
- Estatísticas detalhadas por simulação

### 5. Revisão Abrangente

Sistema de resumos para revisão antes de novos conteúdos:

- Resumos em markdown para cada "parte" estudada
- Visualização rápida do progresso
- Integração com o ciclo de estudo diário

## Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip (gerenciador de pacotes Python)
- Navegador web moderno

### Passo a Passo

1. **Clone ou baixe o projeto**:
   ```bash
   cd estudo_alego
   ```

2. **Crie e ative o ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute a aplicação**:
   ```bash
   python src/main.py
   ```

5. **Acesse no navegador**:
   ```
   http://localhost:5001
   ```

### Dependências Principais

```
Flask==3.1.1           # Framework web
Flask-SQLAlchemy==3.1.1 # ORM para banco de dados
Flask-CORS==6.0.0      # Suporte a CORS
Werkzeug==3.1.3        # Utilitários WSGI
```

## Guia de Uso

### 1. Criando um Novo Curso

1. Clique em "Novo Curso" na sidebar ou no dashboard
2. Preencha o nome e descrição do curso
3. Defina o número de matérias (1-20)
4. Nomeie cada matéria
5. Clique em "Criar Curso"

### 2. Adicionando Conteúdos

Para cada matéria, você pode adicionar três tipos de conteúdo:

#### PDF
- Clique em "Conteúdo" na matéria desejada
- Selecione "PDF" como tipo
- Faça upload do arquivo
- O sistema armazenará o arquivo com nome único

#### Resumo (Markdown)
- Selecione "Resumo (Markdown)" como tipo
- Digite o conteúdo usando sintaxe Markdown
- Ideal para resumos e anotações

#### Vídeo
- Selecione "Vídeo" como tipo
- Faça upload do arquivo de vídeo
- Formatos suportados: MP4, AVI, MOV, WMV, FLV, WebM

### 3. Criando Flashcards

1. Acesse uma matéria específica
2. Use a funcionalidade de flashcards (em desenvolvimento)
3. Crie perguntas e respostas
4. Defina o nível de dificuldade (1-3)

### 4. Usando a Técnica Feynman

1. Navegue até a seção "Técnica Feynman"
2. Selecione a matéria
3. Crie um novo registro com tópico e explicação
4. Refine suas explicações ao longo do tempo

### 5. Realizando Simulações

1. Acesse "Simulações de Prova"
2. Crie uma nova simulação
3. Adicione questões com alternativas
4. Defina as respostas corretas
5. Execute a simulação e acompanhe o desempenho

## API Documentation

### Endpoints Principais

#### Cursos
```
GET    /api/cursos              # Listar cursos
POST   /api/cursos              # Criar curso
GET    /api/cursos/{id}         # Obter curso específico
PUT    /api/cursos/{id}         # Atualizar curso
DELETE /api/cursos/{id}         # Deletar curso (soft delete)
```

#### Matérias
```
GET    /api/cursos/{id}/materias     # Listar matérias do curso
POST   /api/cursos/{id}/materias     # Criar matéria
PUT    /api/materias/{id}            # Atualizar matéria
DELETE /api/materias/{id}            # Deletar matéria
```

#### Conteúdos
```
GET    /api/materias/{id}/conteudos           # Listar conteúdos
POST   /api/materias/{id}/conteudos           # Criar conteúdo
GET    /api/conteudos/{id}                    # Obter conteúdo
GET    /api/conteudos/{id}/download           # Download de arquivo
PUT    /api/conteudos/{id}/marcar-estudado   # Marcar como estudado
```

#### Flashcards
```
GET    /api/materias/{id}/flashcards     # Listar flashcards
POST   /api/materias/{id}/flashcards     # Criar flashcard
PUT    /api/flashcards/{id}/responder    # Responder flashcard
GET    /api/flashcards/revisar           # Flashcards para revisar
```

#### Simulações
```
GET    /api/cursos/{id}/simulacoes           # Listar simulações
POST   /api/cursos/{id}/simulacoes           # Criar simulação
GET    /api/simulacoes/{id}                  # Obter simulação
PUT    /api/simulacoes/{id}/responder        # Responder simulação
GET    /api/simulacoes/{id}/estatisticas     # Estatísticas da simulação
```

#### Técnica Feynman
```
GET    /api/materias/{id}/feynman     # Listar registros Feynman
POST   /api/materias/{id}/feynman     # Criar registro
GET    /api/feynman/{id}              # Obter registro específico
PUT    /api/feynman/{id}              # Atualizar registro
DELETE /api/feynman/{id}              # Deletar registro
```

### Formato de Resposta

Todas as respostas da API seguem o padrão:

```json
{
  "success": true,
  "message": "Operação realizada com sucesso",
  "data": {
    // Dados específicos da operação
  }
}
```

Em caso de erro:

```json
{
  "success": false,
  "message": "Descrição do erro"
}
```

## Testes

O projeto inclui uma suíte completa de testes unitários usando pytest.

### Executando os Testes

```bash
# Instalar pytest se necessário
pip install pytest pytest-cov

# Executar todos os testes
pytest tests/

# Executar com relatório de cobertura
pytest --cov=src tests/

# Executar testes específicos
pytest tests/test_api.py::TestCursos::test_criar_curso_sucesso
```

### Estrutura dos Testes

Os testes estão organizados em classes por funcionalidade:

- **TestCursos**: Testes para operações CRUD de cursos
- **TestMaterias**: Testes para operações CRUD de matérias  
- **TestConteudos**: Testes para conteúdos e marcação de progresso
- **TestFlashcards**: Testes para flashcards e repetição espaçada
- **TestSimulacoes**: Testes para simulações de prova
- **TestFeynman**: Testes para registros da técnica Feynman

### Fixtures Disponíveis

- `client`: Cliente de teste Flask configurado
- `sample_curso`: Curso de exemplo com matérias
- `sample_materia`: Matéria de exemplo para testes

## Estrutura do Banco de Dados

### Diagrama de Relacionamentos

```
Curso (1) -----> (N) Materia (1) -----> (N) Conteudo
  |                    |
  |                    +-----> (N) Flashcard
  |                    |
  |                    +-----> (N) RegistroFeynman
  |
  +-----> (N) Simulacao (1) -----> (N) QuestaoSimulacao
```

### Modelos Detalhados

#### Curso
- `id`: Chave primária
- `nome`: Nome do curso/concurso
- `descricao`: Descrição opcional
- `data_criacao`: Timestamp de criação
- `ativo`: Flag para soft delete

#### Materia
- `id`: Chave primária
- `nome`: Nome da matéria
- `descricao`: Descrição opcional
- `ordem`: Ordem de exibição
- `curso_id`: Chave estrangeira para Curso
- `ativo`: Flag para soft delete

#### Conteudo
- `id`: Chave primária
- `titulo`: Título do conteúdo
- `tipo`: Tipo (pdf, markdown, video)
- `arquivo_path`: Caminho do arquivo (se aplicável)
- `conteudo_texto`: Texto em markdown (se aplicável)
- `ordem`: Ordem de exibição
- `estudado`: Flag de progresso
- `data_estudo`: Timestamp do estudo
- `materia_id`: Chave estrangeira para Materia

#### Flashcard
- `id`: Chave primária
- `pergunta`: Texto da pergunta
- `resposta`: Texto da resposta
- `dificuldade`: Nível de dificuldade (1-3)
- `acertos`: Contador de acertos
- `erros`: Contador de erros
- `ultima_revisao`: Timestamp da última revisão
- `proxima_revisao`: Timestamp da próxima revisão
- `materia_id`: Chave estrangeira para Materia

## Personalização e Extensão

### Adicionando Novas Funcionalidades

1. **Novos Modelos**: Adicione em `src/models/estudo.py`
2. **Novas Rotas**: Crie blueprints em `src/routes/`
3. **Frontend**: Modifique `src/static/app.js` para novas interações
4. **Estilos**: Adicione CSS em `src/static/styles.css`

### Configurações Avançadas

#### Banco de Dados
Para usar PostgreSQL ou MySQL em produção:

```python
# Em src/main.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

#### Upload de Arquivos
Configurar limites e tipos permitidos:

```python
# Em src/routes/conteudos.py
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'avi', 'mov'}
```

#### CORS
Configurar origens permitidas:

```python
# Em src/main.py
CORS(app, origins=['http://localhost:3000', 'https://meudominio.com'])
```

## Segurança

### Medidas Implementadas

1. **Validação de Entrada**: Todos os endpoints validam dados de entrada
2. **Sanitização de Arquivos**: Nomes de arquivo são sanitizados com `secure_filename`
3. **Soft Delete**: Registros são marcados como inativos, não deletados
4. **CORS Configurado**: Controle de acesso entre origens
5. **Validação de Tipos**: Verificação de tipos de arquivo no upload

### Recomendações para Produção

1. **HTTPS**: Use sempre HTTPS em produção
2. **Autenticação**: Implemente sistema de login/senha
3. **Rate Limiting**: Limite requisições por IP
4. **Backup**: Configure backup automático do banco
5. **Logs**: Implemente logging detalhado
6. **Firewall**: Configure firewall adequadamente

## Performance

### Otimizações Implementadas

1. **Lazy Loading**: Relacionamentos carregados sob demanda
2. **Índices**: Índices automáticos em chaves estrangeiras
3. **Paginação**: Limite de resultados em listagens
4. **Cache**: Headers de cache para arquivos estáticos

### Monitoramento

Para monitorar performance em produção:

```python
# Adicionar em src/main.py
import time
from flask import g

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start_time
    if diff > 1.0:  # Log requisições lentas
        app.logger.warning(f'Slow request: {request.endpoint} took {diff:.2f}s')
    return response
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Importação de Módulos
```bash
# Solução: Verificar se o ambiente virtual está ativo
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Porta em Uso
```bash
# Solução: Usar porta diferente
# Modificar em src/main.py: app.run(port=5002)
```

#### 3. Erro de Banco de Dados
```bash
# Solução: Recriar banco de dados
rm src/database/app.db
python src/main.py  # Recriará automaticamente
```

#### 4. Upload de Arquivo Falha
- Verificar se a pasta `uploads/` existe
- Verificar permissões de escrita
- Verificar tamanho do arquivo (limite: 100MB)

### Logs e Debugging

Para habilitar logs detalhados:

```python
# Em src/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
```

## Contribuição

### Estrutura para Contribuições

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### Padrões de Código

- **Python**: Seguir PEP 8
- **JavaScript**: Usar ES6+ e JSDoc para documentação
- **CSS**: Usar metodologia BEM para classes
- **Commits**: Usar conventional commits

### Testes

Toda nova funcionalidade deve incluir testes:

```python
def test_nova_funcionalidade(client):
    """Testa a nova funcionalidade implementada."""
    # Arrange
    dados = {'campo': 'valor'}

    # Act
    response = client.post('/api/endpoint', json=dados)

    # Assert
    assert response.status_code == 201
    assert response.json['success'] is True
```

## Roadmap

### Versão 1.1 (Próxima)
- [ ] Sistema de autenticação e usuários
- [ ] Relatórios de progresso detalhados
- [ ] Exportação de dados em PDF
- [ ] Notificações de revisão
- [ ] Modo offline

### Versão 1.2 (Futuro)
- [ ] Integração com calendário
- [ ] Gamificação (pontos, badges)
- [ ] Compartilhamento de conteúdo
- [ ] API mobile
- [ ] Análise de desempenho com IA

### Versão 2.0 (Longo Prazo)
- [ ] Aplicativo mobile nativo
- [ ] Colaboração em tempo real
- [ ] Integração com plataformas de vídeo
- [ ] Sistema de recomendações
- [ ] Marketplace de conteúdo

## Licença

Este projeto é desenvolvido para fins educacionais e de estudo. Sinta-se livre para usar, modificar e distribuir conforme necessário.

## Suporte

Para dúvidas, sugestões ou problemas:

1. **Documentação**: Consulte este README
2. **Testes**: Execute a suíte de testes para verificar funcionamento
3. **Logs**: Verifique os logs da aplicação para erros específicos
4. **Código**: O código está amplamente comentado para facilitar compreensão

---

**Desenv
(Content truncated due to size limit. Use line ranges to read in chunks)