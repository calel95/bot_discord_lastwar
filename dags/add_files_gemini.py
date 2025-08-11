from airflow.decorators import dag, task
from pendulum import datetime
from dotenv import load_dotenv
from google import genai

from datetime import datetime, timedelta
import os


load_dotenv()

#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the basic parameters of the DAG, like schedule and start_date
@dag(
    start_date=(datetime.now()),
    schedule=timedelta(hours=48),  # This DAG will run once a day
    catchup=False,
    default_args={"owner": "Astro"},
    tags=["gemini","cleanup"],
)


def upload_gemini_files_dag():
    # Define tasks
    @task
    def upload_files_gemini():
        from src.main import carrega_arquivos_como_fonte
        carrega_arquivos_como_fonte()

    # Use dynamic task mapping to run the print_astronaut_craft task for each
    # Astronaut in space

# Instantiate the DAG
    upload_files_gemini()
upload_gemini_files_dag()
