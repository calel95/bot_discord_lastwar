from airflow.decorators import dag, task
from pendulum import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta
from google import genai
import os


load_dotenv()

#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the basic parameters of the DAG, like schedule and start_date
@dag(
    start_date=(datetime.now()),  # Set a fixed start date for the DAG
    schedule=timedelta(hours=46),  # This DAG will run once a day
    catchup=False,
    default_args={"owner": "Astro"},
    tags=["gemini","cleanup"],
)


def process_full_remove_extract_upload():
    # Define tasks
    @task
    def executar_remocao_arquivos_da_base_gemini():
        from src.utils import remover_todos_arquivos_gemini
        remover_todos_arquivos_gemini()

    @task
    def executar_extracao():
        from src.utils import extract_content_full_urls
        extract_content_full_urls()
    
    @task
    def executar_envio_dos_arquivos_para_gemini():
        from src.utils import carrega_arquivos_como_fonte
        carrega_arquivos_como_fonte()
    
    


    # Use dynamic task mapping to run the print_astronaut_craft task for each
    # Astronaut in space

# Instantiate the DAG
    task1 = executar_remocao_arquivos_da_base_gemini()
    task2 = executar_extracao()
    task3 = executar_envio_dos_arquivos_para_gemini()

    task1 >> task2 >> task3

process_full_remove_extract_upload()