import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from utils import criar_agente_last_war, user_add_source_data, checks_existing_files, help_last_war
import logging
import sentry_sdk
from sentry_sdk import logger as sentry_logger


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    #logging.info(f'Bot logado como {bot.user.name} ({bot.user.id})')
    #sentry_sdk.capture_message(f'Bot logado como {bot.user.name} ({bot.user.id})')
    print('Pronto para receber comandos!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) and not message.mention_everyone:
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if question:
            await message.channel.send(f"Hi {message.author.mention}! Asked me: '{question}'")
            await message.channel.send("I'm processing your question about Last War: Mobile...")

#TODO: Validar o envio da resposta em partes
            try:
                # Utiliza a função da IA importada
                bot_answer = criar_agente_last_war(question=question)
                #sentry_logger.info(bot_answer)
                #await message.channel.send(f"{message.author.mention}, here is the answer: {bot_answer}")
                for part in bot_answer:
                    await message.channel.send(part)

            except Exception as e:
                await message.channel.send(f"Desculpe, {message.author.mention}, houve um erro ao processar sua pergunta: `{e}`")

        return

    await bot.process_commands(message)

# Comandos simples
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

@bot.command(name='test')
async def ping(ctx):
    await ctx.send('Bot in operation!!')

@bot.command(name='aid')
async def help_commands(ctx):
    help_text = help_last_war()
    await ctx.send(help_text)
    #await ctx.send(f"Hi! File name is : '{file_name}'")
    #await ctx.send(f"Type the content to add to the database")

@bot.command(name='input')
async def input_cmd(ctx, file_name):
    #file_name = ctx.message.content.replace('!input', '')
    await ctx.send(f"Hi! File name is : '{file_name}'")
    await ctx.send(f"Type the content to add to the database")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        mensagem = await bot.wait_for('message', check=check, timeout=60)
        user_add_source_data(file_name_input=file_name, message=mensagem.content)
        await ctx.send('Data added successfully!')
    except Exception as e:
        await ctx.send(f'Error or timeout: {e}')

if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
