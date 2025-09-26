# Bot Discord Last War

Um bot do Discord para o jogo Last War: Survival que utiliza Inteligência Artificial (Gemini) para responder perguntas sobre o jogo, também incluído um bot que realiza automaticamente tradução entre inglês e português, com pipeline automatizado de dados usando Apache Airflow.

## Pré-requisitos
- Python 3.12
- Docker e Docker Compose
- API KEY do bot do Discord
- API KEY do Google Gemini AI
- API KEY do Youtube
- API KEY da OpenAI

## Instalação

1 - **Clone o Repositório**
    
    git clone https://github.com/calel95/bot_discord_lastwar.git

2 - **Usando o Poetry**

    #Instala as dependencias
    poetry install

    #ativa ambiente virtual
    poetry shell

3 - **Usando o Docker**

    #executa o docker-compose, onde vai funcionar os schedulers das funções, que fará o ETL.
    #OBS: RODE ESSE COMANDO QUANDO JA TIVER COM O ARQUIVO .ENV COMPLETO COM AS CREDENCIAIS
    docker-compose up -d

## Configuração

1 - **Variáveis de Ambiente**

Crie um arquivo .env na raiz do projeto, preencha apenas o que esta sem valor

    #APIs
    OPENAI_API_KEY=
    GEMINI_API_KEY=
    YOUTUBE_API_KEY=

    #Discord
    DISCORD_TOKEN=
    DISCORD_TOKEN_TRANSLATER=
    

    #Airflow
    AIRFLOW_UID=50000
    _AIRFLOW_WWW_USER_USERNAME=airflow
    _AIRFLOW_WWW_USER_PASSWORD=airflow
    _PIP_ADDITIONAL_REQUIREMENTS=-r /opt/airflow/requirements.txt

2 - **Configuração do Discord**

- Acesse o Discord Developer Portal
- Crie uma nova aplicação
- Vá para a seção "Bot" e crie um bot
- Copie o token e adicione ao `.env`
- Ative as seguintes permissões:
    - Send Messages
    - Read Message History
    - Use Slash Commands
    - Mention Everyone

3 - **APIs Externas**

**Gemini AI**
- Acesse o Google AI Studio
- Gere uma API KEY
- Adicione ao arquivo `.env`

**Youtube Data API**
- Acesse Google Cloud Console

### Executando o bot do Discord
    poetry shell
    python src/main.py

### Executando o Airflow
    docker-compose up -d
    # para acessar a interface http://localhost:8080
    # Usuário: airflow | Senha: airflow

### Comandos do Bot Discord

O bot last_war do Discord realiza diversos comandos basicos e avançados, e para ajudar na utilização, foi criado um "--help", que é utilizado rodando o comando `!aid`, esse comando vai puxar um arquivo --help com instrucoes de uso do bot

### Comandos do Bot Tradutor

O bot_translater do Discord realiza a tradução automática de ingles->portugues e portugues>ingles, em tempo real, e ele existe apenas dois comandos, um de ativar o bot `!start` e outro de desativar o bot `off`

### DAGs do Airflow

As DAGs do Airflow são scheduladas, existe um processo que roda todo o pipeline, e existem mais 3 que são os mesmos processos que roda no pipeline completo, porem de forma apartadas.

1 - `process_full.py` - **Pipeline completo**
- Ele remove os arquivos existentes na base do Gemini, extrai novos conteudos das fontes cadastradas, e carrega para a base do Gemini novamente. Esse processo de carregar as fontes para a base do Gemini é necessário pois os dados ficam armazenados por apenas 48 horas, depois sao removidos automaticamente pelo google, e para garantir que nao fique com dados duplicados eu realizo uma limpeza antes de enviar os dados novamente. Mesmo que o tempo de dados duplicados fosse pequena poderia atrabalhar na performance do bot. Essa dag contem as dags web_scraping_files_web.py, add_files_gemini.py e remove_files_gemini.py
- **Scheduler:** 46 horas

2 - `web_scraping.py` - **Extração Web**
- Faz a extração na web, um scraping do site LastWar Tutorial, e armazena cada pagina do site em um arquivo .txt na pasta /data

3 - `add_files_gemini.py` - **Upload de Arquivos**
- Carrega os arquivos locais da pasta /data para o Gemini File API, a base de dados do Gemini

4 - `remove_files_gemini.py` - **Limpeza**
- Remove todos os arquivos presentes na base de dados do Gemini, do Gemini File API, processo realizado para evitar de ter dados duplicados, pois cada arquivo enviado recebe uma chave unica

### Testes
O projeto possuí testes automatizados do bot simples, usando pytest.O teste Verifica:
- `test_checks_existing_files` - verificação de arquivos existentes
- `test_extract_content_full_urls` -  testa o Web Scraping
- `test_criar_agente_last_war` - testa o agente do Gemini 
- `test_user_add_source_data` - testa o upload de arquivos para o Gemini File API
- `test_help_last_war` - testa a funcao de ajuda !aid

### Para rodar os testes:

    poetry run pytest tests/tests_bot.py


