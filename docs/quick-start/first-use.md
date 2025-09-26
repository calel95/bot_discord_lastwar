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