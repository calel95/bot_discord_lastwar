import discord
from openai import OpenAI
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_TRANSLATER')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)
#openai.api_key = os.getenv('OPENAI_API_KEY')

# Configurações do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

client = discord.Client(intents=intents)

# Função para traduzir o texto usando a API da OpenAI
async def translate_text(text_to_translate):
    try:
        # Define a instrução para o modelo
        response = openai.chat.completions.create(
            model="gpt-5-mini",  # Você pode usar um modelo mais recente se preferir
            messages=[
                {"role": "system", "content": "Você é um tradutor multilíngue. Recebe uma frase e a traduz para o inglês. Se a frase já estiver em inglês, traduza para o português. Mantenha a tradução concisa e direta. Faça apenas a tradução, sem explicações adicionais."},
                {"role": "user", "content": text_to_translate}
            ],
            #temperature=0.3 # Um valor baixo para manter a tradução consistente e literal
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return "Não foi possível traduzir a mensagem. Tente novamente."

# Evento para quando o bot estiver online e pronto
@client.event
async def on_ready():
    print(f'Bot está online como {client.user}')

# Evento para quando uma mensagem é enviada
@client.event
async def on_message(message):
    # Ignora mensagens do próprio bot para evitar loops infinitos
    if message.author == client.user:
        return

    # Se a mensagem começar com o prefixo "!traduzir", o bot executa a tradução
    #if message.content.startswith('!traduzir '):
    texto_original = message.content[len('!traduzir '):].strip()
        
        # Chama a função de tradução
    texto_traduzido = await translate_text(texto_original)
        
        # Responde no chat, mostrando a mensagem original e a tradução
        # await message.channel.send(
        #     f"**Mensagem original:** {texto_original}\n"
        #     f"**Tradução:** {texto_traduzido}"
        # )
    await message.reply(texto_traduzido)
#        await message.channel(texto_traduzido)

# Executa o bot com o seu token
client.run(TOKEN)