# Use a versão do Python 3.12 como base
FROM python:3.12-slim

# Define variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia apenas o arquivo de requisitos primeiro para otimizar o cache do Docker
COPY requirements.txt .

# Atualiza o pip e instala todas as dependências do Python
# Isso vai instalar o FastAPI, Uvicorn, Gunicorn e o Celery (com seu executável)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do seu código da aplicação para o contêiner
COPY . .

# Expõe a porta que a aplicação irá usar
EXPOSE 80

# O comando padrão para iniciar a API. 
# Será substituído pelo 'command' do docker-compose para o worker e beat.
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "app.main:app"]