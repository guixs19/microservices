// frontend/js/upload.js
console.log("🚀 Upload.js carregado!");

// Elementos do DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const configForm = document.getElementById('configForm');
const columnSelect = document.getElementById('columnSelect');
const problemType = document.getElementById('problemType');
const trainBtn = document.getElementById('trainBtn');
const loading = document.getElementById('loading');
const progressFill = document.getElementById('progressFill');
const statusMessage = document.getElementById('statusMessage');

// Verificar se todos os elementos foram encontrados
console.log("Elementos DOM:", {
    uploadArea: !!uploadArea,
    fileInput: !!fileInput,
    fileInfo: !!fileInfo,
    fileName: !!fileName,
    configForm: !!configForm,
    columnSelect: !!columnSelect,
    problemType: !!problemType,
    trainBtn: !!trainBtn,
    loading: !!loading
});

let selectedFile = null;

// Animação GSAP
if (typeof gsap !== 'undefined') {
    gsap.from('.header', {
        duration: 1,
        y: -50,
        opacity: 0,
        ease: 'power3.out'
    });
    console.log("✅ GSAP animação aplicada");
} else {
    console.warn("⚠️ GSAP não carregado");
}

// Eventos de drag and drop
uploadArea.addEventListener('click', () => {
    console.log("📁 Área de upload clicada");
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
    console.log("📁 Arquivo arrastando sobre a área");
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
    console.log("📁 Arquivo saiu da área");
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    console.log("📁 Arquivo solto na área");
    
    const files = e.dataTransfer.files;
    console.log("Arquivos recebidos:", files);
    
    if (files.length > 0) {
        console.log("Primeiro arquivo:", files[0].name, files[0].type, files[0].size);
        handleFile(files[0]);
    } else {
        console.warn("Nenhum arquivo encontrado no drop");
    }
});

fileInput.addEventListener('change', (e) => {
    console.log("📁 Arquivo selecionado via input");
    console.log("Files:", e.target.files);
    
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Processar arquivo selecionado
async function handleFile(file) {
    console.log("📄 Processando arquivo:", file.name, "Tipo:", file.type, "Tamanho:", file.size);
    
    if (!file.name.toLowerCase().endsWith('.csv')) {
        console.error("Arquivo não é CSV:", file.name);
        showAlert('Por favor, selecione um arquivo CSV válido', 'error');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.add('active');
    console.log("✅ Arquivo válido, fileInfo ativado");
    
    // Animar entrada do file info
    if (typeof gsap !== 'undefined') {
        gsap.from(fileInfo, {
            duration: 0.5,
            scale: 0.8,
            opacity: 0,
            ease: 'back.out'
        });
    }

    // Analisar CSV para obter colunas
    await analyzeCSV(file);
}

// Analisar CSV para extrair colunas
async function analyzeCSV(file) {
    console.log("📊 Analisando CSV...");
    const reader = new FileReader();
    
    reader.onload = (e) => {
        console.log("📄 CSV carregado, processando...");
        const csv = e.target.result;
        const lines = csv.split('\n');
        
        console.log(`Linhas encontradas: ${lines.length}`);
        
        if (lines.length > 0) {
            const headers = lines[0].split(',').map(h => h.trim());
            console.log("Cabeçalhos encontrados:", headers);
            
            // Popular select de colunas
            columnSelect.innerHTML = '<option value="">Selecione a coluna alvo</option>';
            headers.forEach(header => {
                const option = document.createElement('option');
                option.value = header;
                option.textContent = header;
                columnSelect.appendChild(option);
            });
            
            configForm.classList.add('active');
            console.log("✅ Formulário de configuração ativado");
            
            // Animar entrada do formulário
            if (typeof gsap !== 'undefined') {
                gsap.from(configForm, {
                    duration: 0.5,
                    y: 30,
                    opacity: 0,
                    ease: 'power3.out',
                    delay: 0.2
                });
            }
        } else {
            console.error("CSV vazio ou inválido");
            showAlert('Arquivo CSV vazio ou inválido', 'error');
        }
    };
    
    reader.onerror = (error) => {
        console.error("Erro ao ler arquivo:", error);
        showAlert('Erro ao ler arquivo', 'error');
    };
    
    reader.readAsText(file);
}

// Função para testar conexão com backend
async function testBackendConnection() {
    console.log("🔍 Testando conexão com backend...");
    try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend conectado:', data);
            return true;
        } else {
            console.error('❌ Backend respondeu com status:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ Backend não disponível:', error);
        showAlert('Backend não está respondendo. Verifique se o servidor está rodando em http://localhost:8000', 'error');
        return false;
    }
}

// Modificar o evento de clique do botão treinar
trainBtn.addEventListener('click', async () => {
    console.log("🎯 Botão treinar clicado");
    
    if (!selectedFile) {
        console.warn("Nenhum arquivo selecionado");
        showAlert('Selecione um arquivo primeiro', 'error');
        return;
    }
    
    if (!columnSelect.value) {
        console.warn("Nenhuma coluna alvo selecionada");
        showAlert('Selecione a coluna alvo', 'error');
        return;
    }
    
    console.log("Arquivo:", selectedFile.name);
    console.log("Coluna alvo:", columnSelect.value);
    console.log("Tipo de problema:", problemType.value);
    
    // Testar conexão primeiro
    const backendOk = await testBackendConnection();
    if (!backendOk) {
        return;
    }
    
    // Mostrar loading
    configForm.style.display = 'none';
    loading.classList.add('active');
    
    // Animar loading
    if (typeof gsap !== 'undefined') {
        gsap.from(loading, {
            duration: 0.5,
            scale: 0.8,
            opacity: 0,
            ease: 'back.out'
        });
    }
    
    try {
        console.log('📤 Iniciando upload do arquivo:', selectedFile.name);
        statusMessage.textContent = 'Enviando arquivo...';
        progressFill.style.width = '10%';
        
        // Fazer upload
        const uploadData = await api.uploadFile(
            selectedFile,
            columnSelect.value,
            problemType.value
        );
        
        console.log('✅ Upload realizado com sucesso:', uploadData);
        statusMessage.textContent = 'Upload concluído! Iniciando treinamento...';
        progressFill.style.width = '30%';
        
        // Polling de status
        console.log('🔄 Iniciando polling de status para job:', uploadData.job_id);
        api.pollStatus(
            uploadData.job_id,
            (progress, message) => {
                console.log(`📊 Progresso: ${progress}% - ${message}`);
                progressFill.style.width = `${progress}%`;
                statusMessage.textContent = message || 'Treinando modelos...';
            },
            (results) => {
                console.log('✅ Treinamento concluído com resultados:', results);
                // Sucesso - redirecionar para dashboard
                window.location.href = `dashboard.html?job_id=${uploadData.job_id}`;
            },
            (error) => {
                console.error('❌ Erro no treinamento:', error);
                showAlert(error.message, 'error');
                loading.classList.remove('active');
                configForm.style.display = 'block';
            }
        );
        
    } catch (error) {
        console.error('❌ Erro no processo:', error);
        showAlert(error.message, 'error');
        loading.classList.remove('active');
        configForm.style.display = 'block';
    }
});

// Testar conexão ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    console.log("📄 Página carregada, testando conexão...");
    testBackendConnection();
});

// Mostrar alerta
function showAlert(message, type = 'info') {
    console.log(`🔔 Alerta [${type}]:`, message);
    
    // Remover alerta existente
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) oldAlert.remove();
    
    // Criar novo alerta
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.querySelector('.upload-container').prepend(alert);
    
    // Animar entrada
    if (typeof gsap !== 'undefined') {
        gsap.from(alert, {
            duration: 0.5,
            x: -100,
            opacity: 0,
            ease: 'power3.out'
        });
    }
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (typeof gsap !== 'undefined') {
            gsap.to(alert, {
                duration: 0.5,
                x: -100,
                opacity: 0,
                ease: 'power3.in',
                onComplete: () => alert.remove()
            });
        } else {
            alert.remove();
        }
    }, 5000);
}