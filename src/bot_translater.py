import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_TRANSLATER')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

# Configurações do Discord
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

status = True

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
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return "Não foi possível traduzir a mensagem. Tente novamente."

# Evento para quando o bot estiver online e pronto
@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}')

# Evento para quando uma mensagem é enviada
@bot.command(name='start')
async def start_translater(ctx):
    global status
    status = True
    await ctx.send("Tradução automática **ligada**.")

# Comando para DESLIGAR a tradução automática
@bot.command(name='off')
async def off_translater(ctx):
    global status
    status = False
    await ctx.send("Tradução automática **desligada**.")

@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot para evitar loops infinitos
    global status
    if message.author == bot.user:
        return

    texto_original = message.content

    if status:
        
        # Chama a função de tradução
        texto_traduzido = await translate_text(texto_original)
                
        await message.reply(texto_traduzido)

    await bot.process_commands(message)
        

# Executa o bot com o seu token
bot.run(TOKEN)