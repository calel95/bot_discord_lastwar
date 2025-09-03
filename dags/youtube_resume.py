from __future__ import annotations
from airflow.decorators import dag, task
from pendulum import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pendulum
from airflow.models.dagrun import DagRun


load_dotenv()

#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the basic parameters of the DAG, like schedule and start_date
@dag(
    start_date=(datetime.now()),  # Set a fixed start date for the DAG
    schedule=None,  # This DAG will run once a day
    catchup=False,
    default_args={"owner": "Astro"},
    tags=["gemini","cleanup"],
)


def youtube_resume_dag():
    """
    Recebe URL do youtube, onde a IA do Gemini irá fazer um resumo do vídeo e armazenar em um arquivo.txt na pasta /data.

    Args:
        video_urls: url[List]: URL do vídeo no Youtube, pode ser mais de uma.

    Exemplo de args no Json de input do Airflow:
        {
    "url": "https://www.youtube.com/watch?v=3t9wD6ribps"
}
    """    

    @task
    def executar_resumo_youtube(dag_run: DagRun):
        from src.utils import extract_content_video_youtube
        if dag_run and dag_run.conf and "url" in dag_run.conf:
            url = dag_run.conf['url'] 
            print(f"URL recebida: {url}")
            extract_content_video_youtube(video_urls=[url])
        else:
            print("Nenhuma URL foi fornecida na configuração.")


# Instantiate the DAG
    executar_resumo_youtube()
youtube_resume_dag()