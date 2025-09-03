from airflow.decorators import dag, task
from pendulum import datetime
from dotenv import load_dotenv
from google import genai
from datetime import datetime, timedelta


load_dotenv()

#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the basic parameters of the DAG, like schedule and start_date
@dag(
    start_date=(datetime.now()),  # Set a fixed start date for the DAG
    schedule=timedelta(hours=47),  # This DAG will run once a day
    catchup=False,
    default_args={"owner": "Astro"},
    tags=["gemini","cleanup"],
)


def remove_gemini_files_dag():
    # Define tasks
    @task
    def executar_remocao():
        from src.utils import remover_todos_arquivos_gemini
        remover_todos_arquivos_gemini()

    # Use dynamic task mapping to run the print_astronaut_craft task for each
    # Astronaut in space

# Instantiate the DAG
    executar_remocao()
remove_gemini_files_dag()
