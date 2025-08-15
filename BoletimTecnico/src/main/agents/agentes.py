from dotenv import load_dotenv
load_dotenv()
import os
from pathlib import Path
import httpx
import openai
from openai import AsyncOpenAI
from .prompts import prompt_scrape, prompt_analise

dotenv_path = Path(__file__).resolve().parents[2] / "target" / ".env"
load_dotenv(dotenv_path=dotenv_path)

async_client = httpx.AsyncClient(verify=False)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_BOLETIM"),
    http_client=async_client
)

async def Agente_Formatador(dadosScrape):
    """
    Agente responsável por formatar os dados do scrape em JSON estruturado.
    """
    try:
        print("Tentando formatar com o modelo gpt-4o-mini...")
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_scrape(dadosScrape)}
            ],
        )
        return response.choices[0].message.content
    except openai.BadRequestError as e:
        if hasattr(e, 'response') and e.response and hasattr(e.response, 'status_code') and e.response.status_code == 400:
            print(f"Erro 400 com gpt-4o-mini (possível estouro de tokens): {e.message}")
            print("Tentando novamente com o modelo gpt-4.1-nano-2025-04-14...")
            try:
                response_retry = await client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[
                        {"role": "user", "content": prompt_scrape(dadosScrape)}
                    ],
                )
                return response_retry.choices[0].message.content
            except Exception as e_retry:
                return f"Erro ao formatar dados com gpt-4.1-mini-2025-04-14 após falha inicial: {e_retry}"
        else:
            return f"Erro da API OpenAI (BadRequest não 400): {e}"
    except Exception as e:
        return f"Erro ao formatar dados: {e}"


async def Agente_Analisador(jsonNovo, jsonAtual):
    """
    Agente responsável por analisar os dados.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_analise(jsonNovo, jsonAtual)}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao analisar dados: {e}"

