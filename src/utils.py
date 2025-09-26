import os
import sys
from dotenv import load_dotenv
from urllib.parse import urljoin
from google import genai
from google.genai import types
from google.api_core import exceptions
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import discord
from discord.ext import commands
from googleapiclient.discovery import build
import time
import asyncio
import sentry_sdk
from sentry_sdk import logger as logger
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

#print(dir(genai))
# --- Configuração da API Key ---
load_dotenv()

sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Captura logs de info para cima
    event_level=logging.ERROR  # Envia logs de error para o Sentry como eventos
)

sentry_sdk.init(
    dsn="https://046dade897743af5d5a949458353ce6c@o4509353079865344.ingest.us.sentry.io/4510071692328960",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    integrations=[sentry_logging],
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    # enable_logs=True,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)



# YouTube Data API

def checks_existing_files():
    """
    Faz a checagem se existe arquivos carregados no Gemini File API.
    Returns:
        int: A quantidade de arquivos no Gemini File API.
    """

    arquivos_existentes = list(client.files.list())

    logging.info("Essa mensagem de log será enviada para o Sentry.")
    

    return len(arquivos_existentes)
    
    

# Buscar vídeos de um canal
def extract_content_video_youtube(channel_id=None, video_urls=None, max_videos=5):
    """
    Processa vídeos do YouTube diretamente com Gemini e salva como arquivos de texto.
    
    Args:
        channel_id (str): ID do canal (opcional)
        video_urls (list): Lista de URLs de vídeos específicos (opcional)
        max_videos (int): Número máximo de vídeos para processar do canal, se tiver channel_id (padrão: 5)
    Returns:
        None, os arquivos são salvos na pasta 'data' com prefixo YOUTUBE-
    """
    
    video_list = []
    video_titles = []
    
    if channel_id and YOUTUBE_API_KEY:
        # Buscar vídeos do canal
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        try:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=max_videos,
                order='date',
                type='video'
            )
            response = request.execute()
            
            for video in response['items']:
                video_id = video['id']['videoId']
                video_title = video['snippet']['title']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_list.append(video_url)
                video_titles.append(video_title)
                
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos do canal: {e}")
            return
    
    if video_urls:
        # Aqui assume-se que você já sabe a URL do vídeo
        for url in video_urls:
            try:
                # Se quiser buscar o título pela API:
                youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
                video_id = url.split('watch?v=')[1].split('&')[0]
                request = youtube.videos().list(
                    part='snippet',
                    id=video_id
                )
                response = request.execute()
                video_title = response['items'][0]['snippet']['title']
                
                video_list.append(url)
                video_titles.append(video_title)
            except Exception as e:
                logger.error(f"Erro ao buscar dados do vídeo: {e}")
                return
    # Criar pasta para dados processados pelo Gemini
    #gemini_data_path = Path('./data/gemini_youtube')
    #gemini_data_path.mkdir(parents=True, exist_ok=True)
    
    for i, video_url in enumerate(video_list):
        try:
            logger.info(f"Processando vídeo {video_url} - {video_titles[i]}")
            
            # Processar vídeo com Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {"text": "Analise este vídeo do YouTube e forneça um resumo detalhado do conteúdo destacando os pontos principais"},
                    {"file_data": {"mime_type": "text/plain", "file_uri": video_url}}
                ],
                config={
                    "temperature": 0.3,
                }
            )
            
            # Extrair ID do vídeo da URL
            video_id = video_url.split('watch?v=')[1].split('&')[0] if 'watch?v=' in video_url else f"video_{video_title}"
            
            filename = f"data/YOUTUBE-{video_titles[i].replace("?","").replace("/","")}_{video_id}.txt"
            
            with open(filename, "w", encoding="utf-8") as arquivo:
                arquivo.write(f"URL DO VÍDEO: {video_url}\n\n")
                arquivo.write("CONTEÚDO PROCESSADO PELO GEMINI:\n\n")
                arquivo.write(response.text)
            
            logger.info(f"Vídeo processado e salvo em: {filename}")
            
            # Pausa para evitar rate limiting
            time.sleep(2)
            
        except Exception as e:
            #print(f"Erro ao processar vídeo {video_url}: {e}")
            logger.error(f"Erro ao processar vídeo {video_url}: {e}")
            #sentry_sdk.capture_message(f"Erro ao processar vídeo {video_url}: {e}")
            continue
    

def extract_content_full_urls():
    """
    Extrai conteúdo de URLs do site Last War Tutorial e salva em arquivos de texto localmente.
    """
    base_url = "https://www.lastwartutorial.com"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    menu_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        # Filtrar apenas links internos relevantes do menu
        full_url = urljoin(base_url, href)
        if  ".com/" in full_url and not "#" in full_url and not "play.google.com" in full_url and not "apps.apple.com" in full_url:
            menu_links.append(full_url)

    if not os.path.exists("data"):
        os.makedirs("data")

    for  url in menu_links:
        response = requests.get(url)
        section_soup = BeautifulSoup(response.text, "html.parser")
        #print(section_soup) #pega todo o html da pagina principal
       
        trata_nome_url = (url.split('.com/', 1)[1]).replace('/', '')
        if not trata_nome_url:
            trata_nome_url = "index"
        nome_do_arquivo = f"data/{trata_nome_url}.txt"

        with open(nome_do_arquivo, "w", encoding="utf-8") as arquivo:
            for section in section_soup:
                texto = section.get_text(strip=True)
                if texto:  # evitar escrever vazios
                    arquivo.write(texto + "\n\n")

        logger.info(f"Arquivo '{nome_do_arquivo}' salvo com sucesso!")

def carrega_arquivos_como_fonte():
    """
    Carrega arquivos de texto da pasta 'data' para o Gemini File API.
    """
    
    caminho_pasta = Path('./data')

    arquivos = [file.name for file in caminho_pasta.iterdir() if file.is_file()]
    arquivos_carregados = []
    client = genai.Client(api_key=GEMINI_API_KEY)


    for file in arquivos:
        uploaded_file = client.files.upload(file=f"{caminho_pasta}/{file}", config={"mime_type": "text/plain"})

        logger.info(f"Arquivo {file} carregado como '{uploaded_file.name}'.  carregado com sucesso!")
        arquivos_carregados.append(uploaded_file)

    logger.info(f"Total de arquivos carregados: {len(arquivos_carregados)}")

    return arquivos_carregados
    
def criar_agente_last_war(question: str):
    """
    Cria um agente LastWar que responde perguntas sobre o jogo Last War: Survival
    usando a API Gemini.
    A função espera que os dados de base já estejam carregados no Gemini File API. Qualquer coisa enviar os dados local antes
    Args:
        question (str): A pergunta do usuário.
    Returns:
        str: A resposta gerada pelo agente Gemini em partes se maior que 1900 caracteres.
    """
    arquivos_existentes = list(client.files.list())


    try:
        prompt = (
            "You are an expert in Last War: Survival. "
            "Answer based ONLY on the information in the documents provided. "
            f"Question: {question}"
        )

        content_parts = [prompt] + arquivos_existentes


        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content_parts,
            config={           
                #"max_output_tokens": 500,
                "temperature": 0.7,
            }
        )

        resposta_chat = response.text

        logger.info("\nResposta do Agente LastWar:")
        logger.info(resposta_chat)
        logger.info("-" * 50)
    except exceptions.PermissionDenied as e:
        logger.error(f"Erro de permissão ou arquivos fonrtes nao encontrados: {e}")
        resposta_chat = "Sorry, missing permission or files not found in source."

    resposta_teste = "Eu quero que seja separado essa resposta em partes"

    if len(resposta_chat) <= 1900:
        return [resposta_chat]
    else:
        #return [resposta_chat[i:i+1950] for i in range(0, len(resposta_chat), 1950)]
        pedacos = []

        for i in range(0, len(resposta_chat), 1900):
            pedaco = resposta_chat[i:i+1900]
            pedacos.append(pedaco)
        return pedacos
        

    #return resposta_chat
def remover_todos_arquivos_gemini():
    """
    Remove todos os arquivos carregados no Gemini File API.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    arquivos = list(client.files.list())
    logger.info(f"Encontrados {len(arquivos)} arquivos...")


    for arquivo in arquivos:
        client.files.delete(name=arquivo.name)
        logger.info(f"Arquivo {arquivo.name} removido com sucesso!")

def user_add_source_data(file_name_input, message):
    with open(f"data/{file_name_input}.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(message + "\n\n")

def help_last_war():
    with open("docs/help_last_war.txt", "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
        #print(conteudo)
    return conteudo

if __name__ == "__main__":
    print("Bem-vindo ao Agente LastWar com Gemini!")
    #help_last_war()
    # extract_content_video_youtube(video_urls=["https://www.youtube.com/watch?v=TsuUhPXOnI8"])
    # if DISCORD_TOKEN:
    #    bot.run(DISCORD_TOKEN)
    #user_add_source_data("user_data", "This is a test message added by the user.")
    # x = criar_agente_last_war(question="What is Last War: Survival about?")
    # for part in x:
    #     print(part)

