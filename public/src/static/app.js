/**
 * Aplicação de Gerenciamento de Estudos para Concurso da Alego
 * 
 * Este arquivo contém toda a lógica JavaScript para interação com a API Flask
 * e gerenciamento da interface do usuário.
 */

// Configuração da API
const API_BASE_URL = 
'/api';

// Estado global da aplicação
const AppState = {
    currentSection: 'dashboard',
    currentCurso: null,
    currentMateria: null,
    cursos: [],
    flashcardsRevisao: [],
    currentFlashcardIndex: 0,
    currentConteudo: null // Adicionado para armazenar o conteúdo sendo visualizado/editado
};

// Utilitários
const Utils = {
    /**
     * Faz uma requisição HTTP para a API
     * @param {string} endpoint - Endpoint da API
     * @param {object} options - Opções da requisição (method, body, etc.)
     * @returns {Promise} - Promise com a resposta da API
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('Erro na API:', error);
            this.showToast(error.message, 'error');
            throw error;
        }
    },

    /**
     * Faz upload de arquivo para a API
     * @param {string} endpoint - Endpoint da API
     * @param {FormData} formData - Dados do formulário com arquivo
     * @returns {Promise} - Promise com a resposta da API
     */
    async uploadFile(endpoint, formData) {
        const url = `${API_BASE_URL}${endpoint}`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Erro no upload');
            }

            return data;
        } catch (error) {
            console.error('Erro no upload:', error);
            this.showToast(error.message, 'error');
            throw error;
        }
    },

    /**
     * Exibe uma notificação toast
     * @param {string} message - Mensagem a ser exibida
     * @param {string} type - Tipo da notificação (success, error, warning)
     */
    showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        // Remove o toast após 5 segundos
        setTimeout(() => {
            toast.remove();
        }, 5000);
    },

    /**
     * Exibe/oculta o loading spinner
     * @param {boolean} show - Se deve exibir ou ocultar
     */
    showLoading(show = true) {
        const loading = document.getElementById('loading');
        loading.classList.toggle('active', show);
    },

    /**
     * Formata uma data para exibição
     * @param {string} dateString - String da data
     * @returns {string} - Data formatada
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    },

    /**
     * Formata uma data e hora para exibição
     * @param {string} dateString - String da data
     * @returns {string} - Data e hora formatadas
     */
    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    }
};

// Gerenciador de Navegação
const Navigation = {
    /**
     * Inicializa a navegação
     */
    init() {
        // Event listeners para os botões de navegação
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.target.closest('.nav-btn').dataset.section;
                this.navigateTo(section);
            });
        });
    },

    /**
     * Navega para uma seção específica
     * @param {string} sectionName - Nome da seção
     */
    navigateTo(sectionName) {
        // Atualizar estado
        AppState.currentSection = sectionName;

        // Atualizar navegação ativa
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Mostrar seção correspondente
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionName).classList.add('active');

        // Carregar dados da seção se necessário
        this.loadSectionData(sectionName);
    },

    /**
     * Carrega dados específicos da seção
     * @param {string} sectionName - Nome da seção
     */
    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'dashboard':
                await Dashboard.load();
                break;
            case 'cursos':
                await Cursos.load();
                break;
            case 'flashcards':
                await Flashcards.load();
                break;
            case 'simulacoes':
                await Simulacoes.load();
                break;
            case 'feynman':
                await Feynman.load();
                break;
        }
    }
};

// Gerenciador do Dashboard
const Dashboard = {
    /**
     * Carrega os dados do dashboard
     */
    async load() {
        try {
            Utils.showLoading(true);

            // Carregar estatísticas
            await this.loadStats();
            await this.loadRecentActivity();

        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Carrega as estatísticas do dashboard
     */
    async loadStats() {
        try {
            // Carregar cursos
            const cursosData = await Utils.apiRequest('/cursos');
            const totalCursos = cursosData.cursos ? cursosData.cursos.length : 0;
            document.getElementById('total-cursos').textContent = totalCursos;

            // Carregar flashcards para revisar
            const flashcardsData = await Utils.apiRequest('/flashcards/revisar');
            const totalFlashcards = flashcardsData.total || 0;
            document.getElementById('total-flashcards').textContent = totalFlashcards;

            // TODO: Implementar contadores de simulações e registros Feynman
            document.getElementById('total-simulacoes').textContent = '0';
            document.getElementById('total-feynman').textContent = '0';

        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    },

    /**
     * Carrega a atividade recente
     */
    async loadRecentActivity() {
        const container = document.getElementById('atividade-recente');

        // Por enquanto, exibir uma mensagem placeholder
        container.innerHTML = `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-info"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Bem-vindo ao seu gerenciador de estudos!</div>
                    <div class="activity-time">Comece criando um novo curso</div>
                </div>
            </div>
        `;
    }
};

// Gerenciador de Cursos
const Cursos = {
    /**
     * Carrega a lista de cursos
     */
    async load() {
        try {
            Utils.showLoading(true);

            const data = await Utils.apiRequest('/cursos');
            AppState.cursos = data.cursos || [];

            this.renderSidebar();
            this.renderContent();

        } catch (error) {
            console.error('Erro ao carregar cursos:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Renderiza a sidebar com a lista de cursos
     */
    renderSidebar() {
        const container = document.getElementById('lista-cursos');

        if (AppState.cursos.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <p>Nenhum curso cadastrado</p>
                    <p>Clique em "Novo Curso" para começar</p>
                </div>
            `;
            return;
        }

        container.innerHTML = AppState.cursos.map(curso => `
            <div class="curso-item ${AppState.currentCurso?.id === curso.id ? 'active' : ''}" 
                 data-curso-id="${curso.id}">
                <div class="curso-nome">${curso.nome}</div>
                <div class="curso-materias">${curso.total_materias} matérias</div>
            </div>
        `).join('');

        // Event listeners para seleção de curso
        container.querySelectorAll('.curso-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const cursoId = parseInt(e.target.closest('.curso-item').dataset.cursoId);
                this.selectCurso(cursoId);
            });
        });
    },

    /**
     * Seleciona um curso específico
     * @param {number} cursoId - ID do curso
     */
    async selectCurso(cursoId) {
        try {
            Utils.showLoading(true);

            const data = await Utils.apiRequest(`/cursos/${cursoId}`);
            AppState.currentCurso = data.curso;

            this.renderSidebar();
            this.renderContent();

        } catch (error) {
            console.error('Erro ao selecionar curso:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Renderiza o conteúdo principal dos cursos
     */
    renderContent() {
        const container = document.getElementById('cursos-content');

        if (!AppState.currentCurso) {
            container.innerHTML = `
                <div class="text-center">
                    <h3>Selecione um curso</h3>
                    <p class="text-muted">Escolha um curso na barra lateral para ver suas matérias</p>
                </div>
            `;
            return;
        }

        const curso = AppState.currentCurso;

        container.innerHTML = `
            <div class="curso-content">
                <div class="curso-header">
                    <div class="curso-info">
                        <h3>${curso.nome}</h3>
                        <p>${curso.descricao || 'Sem descrição'}</p>
                    </div>
                    <div class="curso-actions">
                        <button class="btn-secondary" onclick="Cursos.editarCurso(${curso.id})">
                            <i class="fas fa-edit"></i>
                            Editar
                        </button>
                        <button class="btn-danger" onclick="Cursos.deletarCurso(${curso.id})">
                            <i class="fas fa-trash"></i>
                            Deletar
                        </button>
                    </div>
                </div>

                <div class="materias-grid">
                    ${curso.materias ? curso.materias.map(materia => this.renderMateriaCard(materia)).join('') : ''}
                </div>

                <div class="mt-4">
                    <button class="btn-primary" onclick="Cursos.adicionarMateria(${curso.id})">
                        <i class="fas fa-plus"></i>
                        Adicionar Matéria
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Renderiza um card de matéria
     * @param {object} materia - Dados da matéria
     * @returns {string} - HTML do card
     */
    renderMateriaCard(materia) {
        return `
            <div class="materia-card">
                <div class="materia-header">
                    <h4 class="materia-nome">${materia.nome}</h4>
                    <div class="materia-actions">
                        <button class="btn-secondary btn-small" onclick="Cursos.adicionarConteudo(${materia.id})">
                            <i class="fas fa-plus"></i>
                            Conteúdo
                        </button>
                        <button class="btn-secondary btn-small" onclick="Cursos.editarMateria(${materia.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>

                <div class="conteudos-lista">
                    ${materia.conteudos ? materia.conteudos.map(conteudo => this.renderConteudoItem(conteudo)).join('') : ''}
                    ${!materia.conteudos || materia.conteudos.length === 0 ? '<p class="text-muted">Nenhum conteúdo adicionado</p>' : ''}
                </div>

                <div class="mt-4">
                    <small class="text-muted">
                        ${materia.total_conteudos || 0} conteúdos • ${materia.total_flashcards || 0} flashcards
                    </small>
                </div>
            </div>
        `;
    },

    /**
     * Renderiza um item de conteúdo
     * @param {object} conteudo - Dados do conteúdo
     * @returns {string} - HTML do item
     */
    renderConteudoItem(conteudo) {
        const tipoIcon = {
            'pdf': 'PDF',
            'markdown': 'MD',
            'video': 'VID'
        };

        return `
            <div class="conteudo-item">
                <div class="conteudo-info">
                    <div class="conteudo-tipo ${conteudo.tipo}">${tipoIcon[conteudo.tipo] || conteudo.tipo.toUpperCase()}</div>
                    <span class="conteudo-titulo">${conteudo.titulo}</span>
                    ${conteudo.estudado ? '<span class="conteudo-estudado">✓ Estudado</span>' : ''}
                </div>
                <div class="conteudo-actions">
                    <button class="btn-secondary btn-small" onclick="Cursos.visualizarConteudo(${conteudo.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-secondary btn-small" onclick="Cursos.editarConteudo(${conteudo.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${!conteudo.estudado ? `<button class="btn-primary btn-small" onclick="Cursos.marcarEstudado(${conteudo.id})">
                        <i class="fas fa-check"></i>
                    </button>` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Abre o modal para criar novo curso
     */
    novoCurso() {
        const modal = document.getElementById('modal-novo-curso');
        modal.classList.add('active');

        // Gerar inputs para matérias
        this.gerarInputsMaterias();
    },

    /**
     * Gera inputs dinâmicos para as matérias
     */
    gerarInputsMaterias() {
        const numMaterias = document.getElementById('num-materias').value;
        const container = document.getElementById('materias-container');

        container.innerHTML = '';

        for (let i = 1; i <= numMaterias; i++) {
            const div = document.createElement('div');
            div.className = 'form-group';
            div.innerHTML = `
                <label for="materia-${i}">Matéria ${i}</label>
                <input type="text" id="materia-${i}" name="materia-${i}" placeholder="Nome da matéria ${i}">
            `;
            container.appendChild(div);
        }
    },

    /**
     * Cria um novo curso
     * @param {Event} e - Evento do formulário
     */
    async criarCurso(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const numMaterias = document.getElementById('num-materias').value;

            const materias = [];
            for (let i = 1; i <= numMaterias; i++) {
                const nomeMateria = formData.get(`materia-${i}`);
                if (nomeMateria && nomeMateria.trim()) {
                    materias.push(nomeMateria.trim());
                }
            }

            const cursoData = {
                nome: formData.get('nome'),
                descricao: formData.get('descricao'),
                materias: materias
            };

            await Utils.apiRequest('/cursos', {
                method: 'POST',
                body: JSON.stringify(cursoData)
            });

            Utils.showToast('Curso criado com sucesso!');
            this.fecharModal('modal-novo-curso');
            await this.load();

        } catch (error) {
            console.error('Erro ao criar curso:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Fecha um modal
     * @param {string} modalId - ID do modal
     */
    fecharModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('active');

        // Limpar formulário
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    },

    /**
     * Adiciona conteúdo a uma matéria
     * @param {number} materiaId - ID da matéria
     */
    adicionarConteudo(materiaId) {
        AppState.currentMateria = materiaId;
        const modal = document.getElementById('modal-conteudo');
        modal.classList.add('active');
        // Limpar campos do modal de conteúdo
        document.getElementById('conteudo-titulo').value = '';
        document.getElementById('conteudo-tipo').value = 'markdown';
        document.getElementById('conteudo-texto-group').style.display = 'block';
        document.getElementById('conteudo-arquivo-group').style.display = 'none';
        document.getElementById('conteudo-texto').value = '';
        document.getElementById('conteudo-arquivo').value = '';
        document.getElementById('form-conteudo').onsubmit = Cursos.criarConteudo; // Define a função de submit para criar
    },

    /**
     * Cria um novo conteúdo
     * @param {Event} e - Evento do formulário
     */
    async criarConteudo(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const tipo = formData.get('tipo');

            if (tipo === 'markdown') {
                // Conteúdo de texto
                const conteudoData = {
                    titulo: formData.get('titulo'),
                    tipo: tipo,
                    conteudo_texto: formData.get('conteudo_texto')
                };

                await Utils.apiRequest(`/materias/${AppState.currentMateria}/conteudos`, {
                    method: 'POST',
                    body: JSON.stringify(conteudoData)
                });
            } else {
                // Upload de arquivo
                const uploadData = new FormData();
                uploadData.append('titulo', formData.get('titulo'));
                uploadData.append('tipo', tipo);
                uploadData.append('arquivo', formData.get('arquivo'));

                await Utils.uploadFile(`/materias/${AppState.currentMateria}/conteudos`, uploadData);
            }

            Utils.showToast('Conteúdo adicionado com sucesso!');
            this.fecharModal('modal-conteudo');
            await this.selectCurso(AppState.currentCurso.id);

        } catch (error) {
            console.error('Erro ao criar conteúdo:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Marca um conteúdo como estudado
     * @param {number} conteudoId - ID do conteúdo
     */
    async marcarEstudado(conteudoId) {
        try {
            await Utils.apiRequest(`/conteudos/${conteudoId}/marcar-estudado`, {
                method: 'PUT'
            });

            Utils.showToast('Conteúdo marcado como estudado!');
            await this.selectCurso(AppState.currentCurso.id);

        } catch (error) {
            console.error('Erro ao marcar conteúdo:', error);
        }
    },

    /**
     * Visualiza um conteúdo (abre modal ou link)
     * @param {number} conteudoId - ID do conteúdo
     */
    async visualizarConteudo(conteudoId) {
        try {
            Utils.showLoading(true);
            const conteudo = await Utils.apiRequest(`/conteudos/${conteudoId}`);
            AppState.currentConteudo = conteudo.conteudo; // Armazena o conteúdo completo

            const modal = document.getElementById('modal-visualizar-conteudo');
            const tituloModal = document.getElementById('visualizar-titulo');
            const conteudoDisplay = document.getElementById('visualizar-conteudo-display');
            const downloadLink = document.getElementById('visualizar-download-link');

            tituloModal.textContent = AppState.currentConteudo.titulo;
            conteudoDisplay.innerHTML = ''; // Limpa conteúdo anterior
            downloadLink.style.display = 'none'; // Esconde link de download por padrão

            if (AppState.currentConteudo.tipo === 'markdown') {
                // Para markdown, renderiza o texto
                conteudoDisplay.innerHTML = marked.parse(AppState.currentConteudo.conteudo_texto);
            } else if (AppState.currentConteudo.tipo === 'pdf') {
                // Para PDF, exibe um link para download/visualização
                conteudoDisplay.innerHTML = '<p>Clique no link abaixo para visualizar ou baixar o PDF:</p>';
                downloadLink.href = `${API_BASE_URL}/conteudos/${conteudoId}/download`;
                downloadLink.textContent = `Baixar/Visualizar ${AppState.currentConteudo.titulo}.pdf`;
                downloadLink.style.display = 'block';
            } else if (AppState.currentConteudo.tipo === 'video') {
                // Para vídeo, exibe um player de vídeo
                conteudoDisplay.innerHTML = `
                    <video controls width="100%">
                        <source src="${API_BASE_URL}/conteudos/${conteudoId}/download" type="video/mp4">
                        Seu navegador não suporta o elemento de vídeo.
                    </video>
                `;
            }
            modal.classList.add('active');
        } catch (error) {
            console.error('Erro ao visualizar conteúdo:', error);
            Utils.showToast('Erro ao carregar conteúdo para visualização.', 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Abre o modal para editar um conteúdo
     * @param {number} conteudoId - ID do conteúdo
     */
    async editarConteudo(conteudoId) {
        try {
            Utils.showLoading(true);
            const conteudo = await Utils.apiRequest(`/conteudos/${conteudoId}`);
            AppState.currentConteudo = conteudo.conteudo; // Armazena o conteúdo completo

            const modal = document.getElementById('modal-conteudo');
            const form = document.getElementById('form-conteudo');

            // Preencher formulário com dados existentes
            document.getElementById('conteudo-titulo').value = AppState.currentConteudo.titulo;
            document.getElementById('conteudo-tipo').value = AppState.currentConteudo.tipo;

            // Ajustar visibilidade dos campos de acordo com o tipo
            if (AppState.currentConteudo.tipo === 'markdown') {
                document.getElementById('conteudo-texto-group').style.display = 'block';
                document.getElementById('conteudo-arquivo-group').style.display = 'none';
                document.getElementById('conteudo-texto').value = AppState.currentConteudo.conteudo_texto || '';
            } else {
                document.getElementById('conteudo-texto-group').style.display = 'none';
                document.getElementById('conteudo-arquivo-group').style.display = 'block';
                // Não preenche o campo de arquivo por segurança, mas indica que já existe um
                Utils.showToast('Um arquivo já está associado a este conteúdo. Para substituí-lo, selecione um novo arquivo.', 'warning');
            }

            // Mudar a função de submit para atualização
            form.onsubmit = Cursos.atualizarConteudo; 
            modal.classList.add('active');

        } catch (error) {
            console.error('Erro ao carregar conteúdo para edição:', error);
            Utils.showToast('Erro ao carregar conteúdo para edição.', 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Atualiza um conteúdo existente
     * @param {Event} e - Evento do formulário
     */
    async atualizarConteudo(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const tipo = formData.get('tipo');
            const conteudoId = AppState.currentConteudo.id;

            let requestBody;
            let method = 'PUT';
            let isFileUpload = false;

            if (tipo === 'markdown') {
                requestBody = JSON.stringify({
                    titulo: formData.get('titulo'),
                    tipo: tipo,
                    conteudo_texto: formData.get('conteudo_texto')
                });
            } else {
                // Se for arquivo e um novo arquivo foi selecionado, faz upload
                if (formData.get('arquivo') && formData.get('arquivo').size > 0) {
                    requestBody = new FormData();
                    requestBody.append('titulo', formData.get('titulo'));
                    requestBody.append('tipo', tipo);
                    requestBody.append('arquivo', formData.get('arquivo'));
                    isFileUpload = true;
                } else {
                    // Se não for markdown e nenhum novo arquivo, apenas atualiza o título/tipo
                    requestBody = JSON.stringify({
                        titulo: formData.get('titulo'),
                        tipo: tipo
                    });
                }
            }

            if (isFileUpload) {
                await Utils.uploadFile(`/conteudos/${conteudoId}`, requestBody); // Usar uploadFile para PUT com arquivo
            } else {
                await Utils.apiRequest(`/conteudos/${conteudoId}`, {
                    method: method,
                    body: requestBody
                });
            }

            Utils.showToast('Conteúdo atualizado com sucesso!');
            this.fecharModal('modal-conteudo');
            await this.selectCurso(AppState.currentCurso.id);

        } catch (error) {
            console.error('Erro ao atualizar conteúdo:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Edita um curso existente
     * @param {number} cursoId - ID do curso
     */
    async editarCurso(cursoId) {
        try {
            Utils.showLoading(true);
            const curso = await Utils.apiRequest(`/cursos/${cursoId}`);
            AppState.currentCurso = curso.curso;

            const modal = document.getElementById('modal-novo-curso'); // Reutiliza o modal de novo curso
            const form = document.getElementById('form-novo-curso');

            // Preencher formulário
            document.getElementById('curso-nome').value = AppState.currentCurso.nome;
            document.getElementById('curso-descricao').value = AppState.currentCurso.descricao || '';
            document.getElementById('num-materias').value = AppState.currentCurso.materias.length; // Preenche o número de matérias
            this.gerarInputsMaterias(); // Gera os inputs para as matérias

            // Preencher os nomes das matérias existentes
            AppState.currentCurso.materias.forEach((materia, index) => {
                const inputMateria = document.getElementById(`materia-${index + 1}`);
                if (inputMateria) {
                    inputMateria.value = materia.nome;
                }
            });

            // Mudar a função de submit para atualização
            form.onsubmit = Cursos.atualizarCurso; 
            modal.classList.add('active');

        } catch (error) {
            console.error('Erro ao carregar curso para edição:', error);
            Utils.showToast('Erro ao carregar curso para edição.', 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Atualiza um curso existente
     * @param {Event} e - Evento do formulário
     */
    async atualizarCurso(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const cursoId = AppState.currentCurso.id;
            const numMaterias = document.getElementById('num-materias').value;

            const materias = [];
            for (let i = 1; i <= numMaterias; i++) {
                const nomeMateria = formData.get(`materia-${i}`);
                if (nomeMateria && nomeMateria.trim()) {
                    materias.push(nomeMateria.trim());
                }
            }

            const cursoData = {
                nome: formData.get('nome'),
                descricao: formData.get('descricao'),
                materias: materias // Envia as matérias atualizadas
            };

            await Utils.apiRequest(`/cursos/${cursoId}`, {
                method: 'PUT',
                body: JSON.stringify(cursoData)
            });

            Utils.showToast('Curso atualizado com sucesso!');
            this.fecharModal('modal-novo-curso');
            await this.load();

        } catch (error) {
            console.error('Erro ao atualizar curso:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Deleta um curso
     * @param {number} cursoId - ID do curso
     */
    async deletarCurso(cursoId) {
        if (!confirm('Tem certeza que deseja deletar este curso?')) {
            return;
        }
        try {
            Utils.showLoading(true);
            await Utils.apiRequest(`/cursos/${cursoId}`, {
                method: 'DELETE'
            });
            Utils.showToast('Curso deletado com sucesso!');
            AppState.currentCurso = null; // Limpa o curso selecionado
            await this.load();
        } catch (error) {
            console.error('Erro ao deletar curso:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Edita uma matéria existente
     * @param {number} materiaId - ID da matéria
     */
    async editarMateria(materiaId) {
        try {
            Utils.showLoading(true);
            const materia = await Utils.apiRequest(`/materias/${materiaId}`);
            AppState.currentMateria = materia.materia; // Armazena a matéria completa

            const modal = document.getElementById('modal-materia'); // Novo modal para edição de matéria
            const form = document.getElementById('form-materia');

            // Preencher formulário
            document.getElementById('materia-nome-edit').value = AppState.currentMateria.nome;
            document.getElementById('materia-descricao-edit').value = AppState.currentMateria.descricao || '';

            // Mudar a função de submit para atualização
            form.onsubmit = Cursos.atualizarMateria; 
            modal.classList.add('active');

        } catch (error) {
            console.error('Erro ao carregar matéria para edição:', error);
            Utils.showToast('Erro ao carregar matéria para edição.', 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Atualiza uma matéria existente
     * @param {Event} e - Evento do formulário
     */
    async atualizarMateria(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const materiaId = AppState.currentMateria.id;

            const materiaData = {
                nome: formData.get('nome'),
                descricao: formData.get('descricao')
            };

            await Utils.apiRequest(`/materias/${materiaId}`, {
                method: 'PUT',
                body: JSON.stringify(materiaData)
            });

            Utils.showToast('Matéria atualizada com sucesso!');
            this.fecharModal('modal-materia');
            await this.selectCurso(AppState.currentCurso.id);

        } catch (error) {
            console.error('Erro ao atualizar matéria:', error);
        } finally {
            Utils.showLoading(false);
        }
    }
};

// Gerenciador de Flashcards
const Flashcards = {
    /**
     * Carrega os flashcards
     */
    async load() {
        try {
            Utils.showLoading(true);

            const data = await Utils.apiRequest('/flashcards/revisar?limite=20');
            AppState.flashcardsRevisao = data.flashcards || [];
            AppState.currentFlashcardIndex = 0;

            this.renderContent();

        } catch (error) {
            console.error('Erro ao carregar flashcards:', error);
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Renderiza o conteúdo dos flashcards
     */
    renderContent() {
        const container = document.getElementById('flashcards-content');

        if (AppState.flashcardsRevisao.length === 0) {
            container.innerHTML = `
                <div class="text-center">
                    <h3>Nenhum flashcard para revisar</h3>
                    <p class="text-muted">Crie flashcards nas matérias dos seus cursos</p>
                </div>
            `;
            return;
        }

        const flashcard = AppState.flashcardsRevisao[AppState.currentFlashcardIndex];

        container.innerHTML = `
            <div class="flashcard" id="current-flashcard" onclick="Flashcards.flipCard()">
                <div class="flashcard-content" id="flashcard-content">
                    ${flashcard.pergunta}
                </div>
            </div>

            <div class="flashcard-actions" id="flashcard-actions" style="display: none;">
                <button class="btn-danger" onclick="Flashcards.responder(false)">
                    <i class="fas fa-times"></i>
                    Errei
                </button>
                <button class="btn-primary" onclick="Flashcards.responder(true)">
                    <i class="fas fa-check"></i>
                    Acertei
                </button>
            </div>

            <div class="text-center mt-4">
                <p class="text-muted">
                    Flashcard ${AppState.currentFlashcardIndex + 1} de ${AppState.flashcardsRevisao.length}
                </p>
                <p class="text-muted">Clique no card para ver a resposta</p>
            </div>
        `;
    },

    /**
     * Vira o flashcard para mostrar a resposta
     */
    flipCard() {
        const flashcard = document.getElementById('current-flashcard');
        const content = document.getElementById('flashcard-content');
        const actions = document.getElementById('flashcard-actions');

        if (!flashcard.classList.contains('flipped')) {
            const currentFlashcard = AppState.flashcardsRevisao[AppState.currentFlashcardIndex];
            content.textContent = currentFlashcard.resposta;
            flashcard.classList.add('flipped');
            actions.style.display = 'flex';
        }
    },

    /**
     * Registra a resposta do flashcard
     * @param {boolean} acertou - Se o usuário acertou
     */
    async responder(acertou) {
        try {
            const flashcard = AppState.flashcardsRevisao[AppState.currentFlashcardIndex];

            await Utils.apiRequest(`/flashcards/${flashcard.id}/responder`, {
                method: 'PUT',
                body: JSON.stringify({ acertou })
            });

            // Próximo flashcard
            AppState.currentFlashcardIndex++;

            if (AppState.currentFlashcardIndex >= AppState.flashcardsRevisao.length) {
                // Fim da revisão
                const container = document.getElementById('flashcards-content');
                container.innerHTML = `
                    <div class="text-center">
                        <h3>Parabéns! Revisão concluída!</h3>
                        <p class="text-muted">Você revisou todos os flashcards disponíveis</p>
                        <button class="btn-primary mt-4" onclick="Flashcards.load()">
                            <i class="fas fa-refresh"></i>
                            Revisar Novamente
                        </button>
                    </div>
                `;
            } else {
                this.renderContent();
            }

        } catch (error) {
            console.error('Erro ao responder flashcard:', error);
        }
    }
};

// Gerenciador de Simulações
const Simulacoes = {
    /**
     * Carrega as simulações
     */
    async load() {
        const container = document.getElementById('simulacoes-content');
        container.innerHTML = `
            <div class="text-center">
                <h3>Simulações de Prova</h3>
                <p class="text-muted">Funcionalidade em desenvolvimento</p>
                <button class="btn-primary mt-4" onclick="Simulacoes.novaSimulacao()">
                    <i class="fas fa-plus"></i>
                    Nova Simulação
                </button>
            </div>
        `;
    },

    /**
     * Abre o modal para criar nova simulação
     */
    novaSimulacao() {
        const modal = document.getElementById('modal-simulacao');
        modal.classList.add('active');
    },

    /**
     * Cria uma nova simulação
     * @param {Event} e - Evento do formulário
     */
    async criarSimulacao(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const simulacaoData = {
                titulo: formData.get('titulo'),
                descricao: formData.get('descricao'),
                // Questões serão adicionadas em outra etapa ou via API
                questoes: [] 
            };

            await Utils.apiRequest('/simulacoes', {
                method: 'POST',
                body: JSON.stringify(simulacaoData)
            });

            Utils.showToast('Simulação criada com sucesso!');
            Cursos.fecharModal('modal-simulacao');
            await this.load();

        } catch (error) {
            console.error('Erro ao criar simulação:', error);
        } finally {
            Utils.showLoading(false);
        }
    }
};

// Gerenciador Feynman
const Feynman = {
    /**
     * Carrega os registros Feynman
     */
    async load() {
        const container = document.getElementById('feynman-content');
        container.innerHTML = `
            <div class="text-center">
                <h3>Técnica Feynman</h3>
                <p class="text-muted">Funcionalidade em desenvolvimento</p>
                <button class="btn-primary mt-4" onclick="Feynman.novoRegistro()">
                    <i class="fas fa-plus"></i>
                    Novo Registro
                </button>
            </div>
        `;
    },

    /**
     * Abre o modal para criar novo registro Feynman
     */
    novoRegistro() {
        const modal = document.getElementById('modal-feynman');
        modal.classList.add('active');
    },

    /**
     * Cria um novo registro Feynman
     * @param {Event} e - Evento do formulário
     */
    async criarRegistro(e) {
        e.preventDefault();

        try {
            Utils.showLoading(true);

            const formData = new FormData(e.target);
            const registroData = {
                topico: formData.get('topico'),
                explicacao: formData.get('explicacao')
            };

            // Associa ao curso/matéria atual (simplificado por enquanto)
            const materiaId = AppState.currentMateria ? AppState.currentMateria.id : null; // Precisa ser ajustado para selecionar matéria

            if (!materiaId) {
                Utils.showToast('Selecione uma matéria para associar o registro Feynman.', 'error');
                return;
            }

            await Utils.apiRequest(`/materias/${materiaId}/feynman`, {
                method: 'POST',
                body: JSON.stringify(registroData)
            });

            Utils.showToast('Registro Feynman criado com sucesso!');
            Cursos.fecharModal('modal-feynman');
            await this.load();

        } catch (error) {
            console.error('Erro ao criar registro Feynman:', error);
        } finally {
            Utils.showLoading(false);
        }
    }
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', () => {
    Navigation.init();
    Navigation.navigateTo('dashboard'); // Inicia no dashboard

    // Event listener para o botão de fechar modal
    document.querySelectorAll('.modal .close-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const modalId = e.target.closest('.modal').id;
            Cursos.fecharModal(modalId);
        });
    });

    // Event listener para o botão de adicionar novo curso
    document.getElementById('btn-novo-curso').addEventListener('click', () => {
        Cursos.novoCurso();
    });

    // Event listener para o formulário de novo curso
    document.getElementById('form-novo-curso').addEventListener('submit', Cursos.criarCurso);

    // Event listener para o formulário de conteúdo
    document.getElementById('form-conteudo').addEventListener('submit', Cursos.criarConteudo);

    // Event listener para o formulário de simulação
    document.getElementById('form-simulacao').addEventListener('submit', Simulacoes.criarSimulacao);

    // Event listener para o formulário Feynman
    document.getElementById('form-feynman').addEventListener('submit', Feynman.criarRegistro);

    // Event listener para mudança de tipo de conteúdo no modal de conteúdo
    document.getElementById('conteudo-tipo').addEventListener('change', (e) => {
        const tipo = e.target.value;
        if (tipo === 'markdown') {
            document.getElementById('conteudo-texto-group').style.display = 'block';
            document.getElementById('conteudo-arquivo-group').style.display = 'none';
        } else {
            document.getElementById('conteudo-texto-group').style.display = 'none';
            document.getElementById('conteudo-arquivo-group').style.display = 'block';
        }
    });

    // Event listener para fechar o modal de visualização de conteúdo
    document.getElementById('modal-visualizar-conteudo').querySelector('.close-btn').addEventListener('click', () => {
        document.getElementById('modal-visualizar-conteudo').classList.remove('active');
    });

    // Event listener para fechar o modal de edição de matéria
    document.getElementById('modal-materia').querySelector('.close-btn').addEventListener('click', () => {
        document.getElementById('modal-materia').classList.remove('active');
    });

    // Event listener para o formulário de edição de matéria
    document.getElementById('form-materia').addEventListener('submit', Cursos.atualizarMateria);
});

// Biblioteca Marked para renderizar Markdown
// Certifique-se de incluir <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script> no seu HTML


