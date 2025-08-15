import asyncio
import json
from agents.agentes import Agente_Formatador
import os
from config import PATHS

urls = {
    'CTE':  'https://www.cte.fazenda.gov.br/portal/informe.aspx?ehCTG=false&page=0&pagesize=1',
    'ECD':  'http://sped.rfb.gov.br/projeto/show/273',
    'ECF':  'http://sped.rfb.gov.br/projeto/show/269',
    'EFD CONTRIBUICOES': 'http://sped.rfb.gov.br/projeto/show/268',
    'EFD ICMS IPI':      'http://sped.rfb.gov.br/projeto/show/274',
    'EFD REINF':         'http://sped.rfb.gov.br/projeto/show/1196',
    'ESOCIAL':           'https://www.gov.br/esocial/pt-br/documentacao-tecnica',
    'MDFE':              'https://dfe-portal.svrs.rs.gov.br/Mdfe/Documentos',
    'NFCE':              'https://www.nfe.fazenda.gov.br/portal/informe.aspx?ehCTG=false&page=0&pagesize=1',
    'NFE':               'https://www.nfe.fazenda.gov.br/portal/informe.aspx?ehCTG=false&page=0&pagesize=1',
    'NFSE':              'https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/leiaute-e-esquemas-atuais'
}

dados: dict[str, dict] = {}

async def scrape(crawler) -> dict[str, dict]:
    """
    Executa o scraping para todos os módulos usando o crawler compartilhado.
    """

    for chave, url in urls.items():
        result = await crawler.arun(url=url)       
        json_str_cru: str = await Agente_Formatador(result)
        json_str = json_str_cru.replace("```json", "").replace("```", "")
        try:
            dados_json = json.loads(json_str)
        except json.JSONDecodeError:
            print(f"[ERRO JSON] ao converter saída de {chave}:\n{json_str}")
            continue
        
        dados[chave] = dados_json
        await asyncio.sleep(1)
    
    # Usando o caminho configurado no config.py
    caminho = PATHS['json_novo']
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

    return dados

