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


#print(dir(genai))
# --- Configuração da API Key ---
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# YouTube Data API

def checks_existing_files():
    """
    Cria um agente LastWar que responde perguntas sobre o jogo Last War: Survival
    usando a API Gemini.
    A função espera que os dados de base já estejam carregados no Gemini File API. Qualquer coisa enviar os dados local antes
    Args:
        campo (str): A pergunta do usuário.
    Returns:
        str: A resposta gerada pelo agente Gemini.
    """

    #client = genai.Client(api_key=GEMINI_API_KEY)
    arquivos_existentes = list(client.files.list())

    print(f"Encontrados {len(arquivos_existentes)} arquivos carregados.")
    #return print(f"Encontrados {len(arquivos_existentes)} arquivos carregados.")

    return len(arquivos_existentes)
    
    

# Buscar vídeos de um canal
def extract_content_video_youtube(channel_id=None, video_urls=None, max_videos=2):
    """
    Processa vídeos do YouTube diretamente com Gemini e salva como arquivos de texto.
    
    Args:
        channel_id (str): ID do canal (opcional)
        video_urls (list): Lista de URLs de vídeos específicos (opcional)
        max_videos (int): Número máximo de vídeos para processar do canal
    """
    #GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    #client = genai.Client(api_key=GEMINI_API_KEY)
    
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
            print(f"Erro ao buscar vídeos do canal: {e}")
            return
    
    # Criar pasta para dados processados pelo Gemini
    #gemini_data_path = Path('./data/gemini_youtube')
    #gemini_data_path.mkdir(parents=True, exist_ok=True)
    
    for i, video_url in enumerate(video_list):
        try:
            print(f"Processando vídeo {video_url} - {video_titles[i]}")
            
            # Processar vídeo com Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Analise este vídeo do YouTube e forneça um resumo detalhado do conteúdo, "
                    "incluindo pontos principais, estratégias mencionadas, dicas importantes e "
                    "qualquer informação relevante sobre Last War: Survival. "
                    "Organize a informação de forma clara e estruturada:",
                    video_url
                ],
                config={
                    "temperature": 0.3,
                }
            )
            
            # Extrair ID do vídeo da URL
            video_id = video_url.split('watch?v=')[1].split('&')[0] if 'watch?v=' in video_url else f"video_{video_title}"
            
            filename = f"data/YOUTUBE-{video_titles[i]}_{video_id}.txt"
            
            with open(filename, "w", encoding="utf-8") as arquivo:
                arquivo.write(f"URL DO VÍDEO: {video_url}\n\n")
                arquivo.write("CONTEÚDO PROCESSADO PELO GEMINI:\n\n")
                arquivo.write(response.text)
            
            print(f"Vídeo processado e salvo em: {filename}")
            
            # Pausa para evitar rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao processar vídeo {video_url}: {e}")
            continue
    

def extract_content_full_urls():
    """
    Extrai conteúdo de URLs do site Last War Tutorial e salva em arquivos de texto.
    """
    base_url = "https://www.lastwartutorial.com"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    menu_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        # Filtrar apenas links internos relevantes do menu
    #if any(section in href for section in ['heroes', 'squads', 'buildings']):
        full_url = urljoin(base_url, href)
        if  ".com/" in full_url and not "#" in full_url and not "play.google.com" in full_url and not "apps.apple.com" in full_url:
            #print(full_url)
            menu_links.append(full_url)

    #print(menu_links)
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
                    #print(texto)  # se quiser ver o que está salvando

        print(f"Arquivo '{nome_do_arquivo}' salvo com sucesso!")

def carrega_arquivos_como_fonte():
    
    caminho_pasta = Path('./data')

    arquivos = [file.name for file in caminho_pasta.iterdir() if file.is_file()]
    arquivos_carregados = []
    client = genai.Client()


    for file in arquivos:
        uploaded_file = client.files.upload(file=f"{caminho_pasta}/{file}", config={"mime_type": "text/plain"})
        print(f"Arquivo {file} carregado como '{uploaded_file.name}'.  carregado com sucesso!")
        #sys.stdout.flush()
        arquivos_carregados.append(uploaded_file)

    print(f"Total de arquivos carregados: {len(arquivos_carregados)}")

    return arquivos_carregados
    

def criar_agente_last_war(question: str):
    """
    Cria um agente LastWar que responde perguntas sobre o jogo Last War: Survival
    usando a API Gemini.
    A função espera que os dados de base já estejam carregados no Gemini File API. Qualquer coisa enviar os dados local antes
    Args:
        campo (str): A pergunta do usuário.
    Returns:
        str: A resposta gerada pelo agente Gemini.
    """
    #GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    #genai.configure(api_key=GEMINI_API_KEY)
    #client = genai.Client(api_key=GEMINI_API_KEY)
    #model = genai.GenerativeModel("gemini-2.5-flash")
    #arquivos_existentes = list(client.files.list())
    #print(arquivos_existentes)

    # if not arquivos_existentes:
    #     print("Nenhum arquivo carregado. Carregando arquivos...")
    #     arquivos_existentes = carrega_arquivos_como_fonte()

    #print(f"Encontrados {len(arquivos_existentes)} arquivos carregados.")
    #question = input("Digite sua pergunta sobre LastWar: ")

    # prompt = (
    #     "Você é um especialista em Last War: Survival. "
    #     "Responda baseado APENAS nas informações dos documentos fornecidos. "
    #     f"Pergunta: {question}"
    # )

    try:
        prompt = (
            "You are an expert in Last War: Survival. "
            "Answer based ONLY on the information in the documents provided. "
            f"Question: {question}"
        )

        content_parts = [prompt] + arquivos_existentes

    #     count_tokens = client.models.generate_content(
    #     model="gemini-2.5-flash", contents=prompt
    # )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content_parts,
            config={           
                #"max_output_tokens": 500,
                "temperature": 0.7,
            }
        )

        resposta_chat = response.text
        print("\nResposta do Agente LastWar:")
        print(resposta_chat)
        print("-" * 50)
    except exceptions.PermissionDenied as e:
        print(f"Erro de permissão ou arquivos fonrtes nao encontrados: {e}")
        resposta_chat = "Sorry, missing permission or files not found in source."

    #print(count_tokens.usage_metadata)

    return resposta_chat
def remover_todos_arquivos_gemini():
    """
    Remove todos os arquivos carregados no Gemini File API.
    Ação requer confirmação do usuário no console.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    arquivos = list(client.files.list())
    print(f"Encontrados {len(arquivos)} arquivos...")
    # for arquivo in arquivos:
    #     print(arquivo.name)

    # confirmacao = input("Deseja remover todos os arquivos? (s/n): ")
    # if confirmacao.lower() == 's':
    for arquivo in arquivos:
        client.files.delete(name=arquivo.name)
        print(f"Arquivo {arquivo.name} removido com sucesso!")

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Evento que é disparado quando o bot se conecta ao Discord."""
    print(f'Bot logado como {bot.user.name} ({bot.user.id})')
    print('Pronto para receber comandos!')


@bot.event
async def on_message(message):
    """Evento que é disparado quando uma mensagem é enviada em qualquer canal."""
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if question:
            await message.channel.send(f"Hi {message.author.mention}! Asked me: '{question}'")
            await message.channel.send("I'm processing your question about Last War: Mobile...")

            try:
                # Use sua função de IA aqui
                bot_answer = criar_agente_last_war(question=question)
                await message.channel.send(f"{message.author.mention}, here is the answer: {bot_answer}")

            except Exception as e:
                await message.channel.send(f"Desculpe, {message.author.mention}, houve um erro ao processar sua pergunta: `{e}`")
                print(f"Erro na IA: {e}")
        return

    await bot.process_commands(message)

@bot.command(name='test')
async def ping(ctx):
    """
    Comando de teste para verificar se o bot está online e respondendo.
    Uso: !teste
    """
    await ctx.send('Bot in operation!!')

@bot.command(name='check')
async def carregar_dados_cmd(ctx):
    """Comando para carregar os dados de Last War para o Gemini."""
    await ctx.send("Checking sources...")
    try:
        x = int(checks_existing_files())
        if x > 0:
            await ctx.send(f"Arquives in data source.")
        else:
            await ctx.send("No files found in data source. Please request upload files first.")

    except Exception as e:
        await ctx.send(f"Erro ao checking sources: `{e}`")

if __name__ == "__main__":
    print("Bem-vindo ao Agente LastWar com Gemini!")
