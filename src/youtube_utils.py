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
from discord.ext import commands
from googleapiclient.discovery import build
import time
import asyncio

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_content_video_youtube(channel_id=None, video_urls=None, max_videos=None):
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
                print(f"Erro ao buscar dados do vídeo: {e}")
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
            
            print(f"Vídeo processado e salvo em: {filename}")
            
            # Pausa para evitar rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao processar vídeo {video_url}: {e}")
            continue