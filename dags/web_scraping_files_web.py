from airflow.decorators import dag, task
from pendulum import datetime
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sentry_sdk

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


def web_scraping_files_web_dag():
    # Define tasks
    @task
    def executar_extracao():
        from src.utils import extract_content_full_urls
        extract_content_full_urls()

    # Use dynamic task mapping to run the print_astronaut_craft task for each
    # Astronaut in space

# Instantiate the DAG
    executar_extracao()
web_scraping_files_web_dag()