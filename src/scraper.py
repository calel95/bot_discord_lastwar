import os
import sys
from dotenv import load_dotenv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import time
import asyncio


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