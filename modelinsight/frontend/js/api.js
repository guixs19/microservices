// frontend/js/api.js
// Configuração da API - Use localhost em vez de 127.0.0.1
const API_BASE_URL = 'http://localhost:8000/api';

class ModelInsightAPI {
    constructor() {
        this.baseUrl = API_BASE_URL;
        this.currentJobId = null;
    }

    // Upload de arquivo CSV
    async uploadFile(file, targetColumn, problemType) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_column', targetColumn);
        formData.append('problem_type', problemType);

        try {
            console.log('Enviando arquivo para:', `${this.baseUrl}/upload/`);
            const response = await fetch(`${this.baseUrl}/upload/`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Resposta de erro:', errorText);
                try {
                    const error = JSON.parse(errorText);
                    throw new Error(error.message || 'Erro no upload');
                } catch {
                    throw new Error(`Erro ${response.status}: ${response.statusText}`);
                }
            }

            const data = await response.json();
            console.log('Upload resposta:', data);
            this.currentJobId = data.job_id;
            return data;
        } catch (error) {
            console.error('Erro no upload:', error);
            throw error;
        }
    }

    // Verificar status do treinamento
    async checkStatus(jobId) {
        try {
            console.log('Verificando status:', `${this.baseUrl}/upload/status/${jobId}`);
            const response = await fetch(`${this.baseUrl}/upload/status/${jobId}`);
            
            if (!response.ok) {
                throw new Error('Erro ao verificar status');
            }

            const data = await response.json();
            console.log('Status resposta:', data);
            return data;
        } catch (error) {
            console.error('Erro ao verificar status:', error);
            throw error;
        }
    }

    // Obter resultados do treinamento
    async getResults(jobId) {
        try {
            console.log('Buscando resultados:', `${this.baseUrl}/metrics/${jobId}`);
            const response = await fetch(`${this.baseUrl}/metrics/${jobId}`);
            
            if (!response.ok) {
                throw new Error('Erro ao obter resultados');
            }

            const data = await response.json();
            console.log('Resultados resposta:', data);
            return data;
        } catch (error) {
            console.error('Erro ao obter resultados:', error);
            throw error;
        }
    }

    // Obter detalhes de um modelo específico
    async getModelDetails(jobId, modelName) {
        try {
            console.log('Buscando detalhes do modelo:', `${this.baseUrl}/metrics/${jobId}/model/${modelName}`);
            const response = await fetch(`${this.baseUrl}/metrics/${jobId}/model/${modelName}`);
            
            if (!response.ok) {
                throw new Error('Erro ao obter detalhes do modelo');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao obter detalhes:', error);
            throw error;
        }
    }

    // Fazer predição
    async predict(jobId, features, modelName = null) {
        try {
            let url = `${this.baseUrl}/predict/${jobId}`;
            if (modelName) {
                url += `?model_name=${modelName}`;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ features })
            });

            if (!response.ok) {
                throw new Error('Erro ao fazer predição');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na predição:', error);
            throw error;
        }
    }

    // Polling de status
    async pollStatus(jobId, onProgress, onComplete, onError) {
        const check = async () => {
            try {
                const status = await this.checkStatus(jobId);
                
                if (onProgress) {
                    onProgress(status.progress || 0, status.message || 'Processando...');
                }

                if (status.status === 'completed') {
                    console.log('Treinamento concluído, buscando resultados...');
                    const results = await this.getResults(jobId);
                    onComplete(results);
                } else if (status.status === 'failed') {
                    onError(new Error(status.message || 'Treinamento falhou'));
                } else {
                    // Continuar polling a cada 2 segundos
                    setTimeout(check, 2000);
                }
            } catch (error) {
                console.error('Erro no polling:', error);
                onError(error);
            }
        };

        check();
    }
}

// Criar instância global da API
const api = new ModelInsightAPI();