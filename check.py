import psycopg
import requests
import os
from dotenv import load_dotenv

from explore import download_seasons, download_matches

load_dotenv()


def check():
    model = os.environ["MODEL"]
    prompt = "Who are you?"
    ollama_url = os.environ["OLLAMA_URL"]
    body = {"model": model, "prompt": prompt, "stream": False}

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT version()"
            )

            print(cur.fetchone())

    response = requests.post(f"{ollama_url}/api/generate", json=body).json()
    print(response["response"])


if __name__ == "__main__":
    check()
    download_seasons()
    download_matches()
