FROM apache/airflow:3.0.3

# Muda para root para instalar dependências do sistema (se necessário)
USER root

# Instala dependências do sistema se precisar (exemplo)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# Volta para o usuário airflow
USER airflow

# Copia e instala requirements
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
