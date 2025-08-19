import os
import sys
from dotenv import load_dotenv
from urllib.parse import urljoin
from google import genai
from google.genai import types
from google.api_core import exceptions
import requests
from pathlib import Path
from googleapiclient.discovery import build
import time
import asyncio


#print(dir(genai))
# --- Configuração da API Key ---
load_dotenv()

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


def carrega_arquivos_como_fonte():
    
    caminho_pasta = Path('./data')

    arquivos = [file.name for file in caminho_pasta.iterdir() if file.is_file()]
    arquivos_carregados = []
    client = genai.Client(api_key=GEMINI_API_KEY)


    for file in arquivos:
        uploaded_file = client.files.upload(file=f"{caminho_pasta}/{file}", config={"mime_type": "text/plain"})
        print(f"Arquivo {file} carregado como '{uploaded_file.name}'.  carregado com sucesso!")
        #sys.stdout.flush()
        arquivos_carregados.append(uploaded_file)

    print(f"Total de arquivos carregados: {len(arquivos_carregados)}")

    return arquivos_carregados
    
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


if __name__ == "__main__":
    print("Bem-vindo ao Agente LastWar com Gemini!")
    if DISCORD_TOKEN:
       bot.run(DISCORD_TOKEN)
    #extract_content_full_urls()
