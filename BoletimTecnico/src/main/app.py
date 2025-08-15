from dotenv import load_dotenv
load_dotenv()
import json
import os
import platform
import aiofiles
import asyncio
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from utils.scrape import scrape, urls as urls_modulos
from agents.agentes import Agente_Analisador
from utils.pdf import gerar_boletim_pdf
from utils.enviar_email import enviar_email_com_anexo_pdf, enviar_email_html
from config import PATHS


def parse_date_str(date_str: str) -> datetime:
    """
    Converte uma string de data "DD/MM/YYYY" ou "MM/YYYY" em objeto datetime.
    MM/YYYY é tratado como o primeiro dia do mês.
    """
    parts = date_str.split('/')
    if len(parts) == 3:
        day, month, year = parts
        return datetime(int(year), int(month), int(day))
    elif len(parts) == 2:
        month, year = parts
        return datetime(int(year), int(month), 1)
    else:
        raise ValueError(f"Formato de data inválido: {date_str}")


async def verificacao():

    hoje = datetime.now()
    print(f"[DATA ATUAL DE EXECUÇÃO DO SCRIPT] {hoje.strftime('%d/%m/%Y')}") # Log da data de execução

    json_atual_str = None
    json_novo_str = None    # Leitura dos arquivos JSON
    try:
        async with aiofiles.open(PATHS['json_atual'], mode="r", encoding='utf-8') as f:
            json_atual_str = await f.read()
        async with aiofiles.open(PATHS['json_novo'], mode="r", encoding='utf-8') as f:
            json_novo_str = await f.read()
    except Exception as e:
        print(f"[ERRO ARQUIVO] Erro ao ler arquivos de entrada: {e}")
        return None

    # Parse dos JSONs e remoção do campo 'versao'
    try:
        dados_atual = json.loads(json_atual_str)
        dados_novo = json.loads(json_novo_str)
        dados_atual_sem_versao = {}
        for modulo, lista in dados_atual.items():
            if isinstance(lista, list) and lista and isinstance(lista[0], dict):
                dados_atual_sem_versao[modulo] = [{'data': lista[0].get('data')}]
            else:
                dados_atual_sem_versao[modulo] = lista # Mantém estrutura se não for o esperado

        dados_novo_sem_versao = {}
        for modulo, lista in dados_novo.items():
            if isinstance(lista, list) and lista and isinstance(lista[0], dict):
                dados_novo_sem_versao[modulo] = [{'data': lista[0].get('data')}]
            else:
                dados_novo_sem_versao[modulo] = lista # Mantém estrutura se não for o esperado

    except Exception as e:
        print(f"[ERRO JSON] Falha ao processar JSON de entrada: {e}")
        return None   
    try:
        found_newer = False
        for modulo, lista_novo_data_only in dados_novo_sem_versao.items():
            lista_atual_data_only = dados_atual_sem_versao.get(modulo)

            # Se o módulo não existe no JSON atual, ou se alguma das listas de dados está vazia/malformada,
            # considera-se que há uma mudança potencial a ser analisada pelo agente.
            if not lista_atual_data_only or not lista_novo_data_only:
                found_newer = True
                break

            data_novo_str = lista_novo_data_only[0].get('data')
            data_atual_str = lista_atual_data_only[0].get('data')            # Se não houver data em um dos registros, considera que pode ser uma atualização (para o agente analisar).
            if not data_novo_str or not data_atual_str:
                found_newer = True
                break

            # Tenta converter as strings de data para objetos datetime para comparação.
            try:
                dt_novo = parse_date_str(data_novo_str)
                dt_atual = parse_date_str(data_atual_str)
            except ValueError:
                # Se o formato da data for inesperado e não puder ser parseado,
                # assume que houve uma mudança e passa para o agente analisar.
                print(f"[AVISO PARSE] Formato de data inesperado para o módulo {modulo}. Prosseguindo para análise do agente.")
                found_newer = True
                break            # CONDIÇÃO DE ATUALIZAÇÃO PRINCIPAL:
            # A atualização (found_newer = True) só ocorre se a nova data (dt_novo)
            # for estritamente MAIOR que a data atual (dt_atual).
            if dt_novo > dt_atual:
                found_newer = True
                break

        if not found_newer:
            print("[INFO] Nenhuma data estritamente mais recente encontrada na verificação preliminar.")
            return {"resposta": "sem_atualizacoes", "mensagem": "Não houve mudança na data dos módulos"}

    except Exception as e:
        print(f"[ERRO COMPARAÇÃO INTERNA] Erro durante a comparação de datas: {e}. Prosseguindo para análise do agente.")
        found_newer = True

    # o script prossegue para chamar o Agente_Analisador.   

    json_atual_para_agente_str = json.dumps(dados_atual_sem_versao, ensure_ascii=False)
    json_novo_para_agente_str = json.dumps(dados_novo_sem_versao, ensure_ascii=False)

    try:
        analise_str = await Agente_Analisador(json_novo_para_agente_str, json_atual_para_agente_str)
    except Exception as e:
        print(f"[ERRO AGENTE] Erro ao chamar Agente_Analisador: {e}")
        return None

    analise_formatada_str = analise_str.replace("```json", "").replace("```", "").strip()

    try:
        async with aiofiles.open(PATHS['json_analise'], mode="w", encoding='utf-8') as f:
            await f.write(analise_formatada_str)
        print(f"[INFO] Resultado da análise do agente salvo em {PATHS['json_analise']}")
    except Exception as e:
        print(f"[ERRO ARQUIVO] Erro ao escrever {PATHS['json_analise']}: {e}")

    try:
        resultado_analise = json.loads(analise_formatada_str)
        return resultado_analise
    except Exception as e:
        print(f"[ERRO JSON] Erro ao converter saída final do agente para JSON: {e}")
        print(f"[DEBUG] Saída do agente que causou erro de parse: {analise_formatada_str}")
        return None


def atualizacao(resposta: dict):
    if resposta and resposta.get('resposta') == 'atualizacao_detectada':
        src = PATHS['json_novo']
        dst = PATHS['json_atual']
        pdf_path = PATHS['pdf_output']
        try:
            os.replace(src, dst)
            print(f"[INFO] Arquivo '{dst}' atualizado com sucesso com o conteúdo de '{src}'.")

            with open(dst, 'r', encoding='utf-8') as f:
                json_atual_com_versoes = json.load(f)

            modulos_para_pdf = []
            if 'modulos_atualizados' in resposta:
                for mod_analisado in resposta['modulos_atualizados']:
                    nome_modulo = mod_analisado['modulo']
                    modulo_info_completa = json_atual_com_versoes.get(nome_modulo)
                    versao_nova = "N/A"
                    if modulo_info_completa and isinstance(modulo_info_completa, list) and modulo_info_completa:
                        versao_nova = modulo_info_completa[0].get('versao', "Versão não encontrada")

                    link_modulo = urls_modulos.get(nome_modulo, "#") 

                    modulos_para_pdf.append({
                        "modulo": nome_modulo,
                        "data_anterior": mod_analisado['data_anterior'],
                        "data_nova": mod_analisado['data_nova'],
                        "versao": versao_nova,
                        "link": link_modulo
                    })

            dados_pdf = {
                "resposta": "atualizacao_detectada",
                "modulos_atualizados": modulos_para_pdf
            }
            gerar_boletim_pdf(dados_pdf)
            print(f"[INFO] Boletim PDF gerado em: {pdf_path}")

            # Enviar email
            if platform.system() == "Windows":
                destinatarios = ["email@email.com"]
            else:
                email_destina = os.getenv("EMAIL_TO")
                destinatarios = [email_destina]
        
            assunto_email = f" Boletim Técnico IA - ATUALIZAÇÕES {datetime.now().strftime('%d/%m/%Y')}"

        
            if enviar_email_html(
                assunto=assunto_email,
                dados_html=dados_pdf,
                destinatarios=destinatarios,
                anexar_pdf=False,  
                caminho_anexo_pdf=pdf_path
            ):
                print("[INFO] Email de notificação em HTML enviado com sucesso.")
            else:
                print("[AVISO] Falha ao enviar email HTML. Tentando método alternativo com PDF...")
                corpo_email = "O Boletim Técnico foi atualizado. Verifique o PDF em anexo."
                if enviar_email_com_anexo_pdf(assunto_email, corpo_email, destinatarios, pdf_path):
                    print("[INFO] Email de notificação com PDF anexo enviado com sucesso.")
                else:
                    print("[ERRO] Falha ao enviar email de notificação.")

        except Exception as e:
            print(f"[ERRO ATUALIZAÇÃO/PDF/EMAIL] Falha ao atualizar arquivo, gerar PDF ou enviar e-mail: {e}")

    elif resposta and resposta.get('resposta') == 'sem_atualizacoes':
        print("[INFO] Nenhuma atualização detectada pelo Agente Analisador.")
    elif not resposta:
        print("[ERRO] Processo de verificação retornou None. Nenhuma ação de atualização será realizada.")
    else:
        print(f"[AVISO] Resposta inesperada do processo de verificação: {resposta}")


async def main():
    crawler = AsyncWebCrawler(
        run_config=CrawlerRunConfig(
            mean_delay=2.0,
            max_range=1.0
        )
    )
    await crawler.start()
    try:
        print("[INFO] Iniciando processo de scraping...")
        await scrape(crawler)
        print(f"[INFO] Scraping concluído. Resultado salvo em {PATHS['json_novo']}.")

        print("[INFO] Iniciando processo de verificação de atualizações...")
        resultado_verificacao = await verificacao()

        if resultado_verificacao:
            print(f"[INFO] Resultado da verificação: {resultado_verificacao.get('resposta')}")
            atualizacao(resultado_verificacao)
        else:
            print("[ERRO] Falha no processo de verificação. Verifique os logs de erro.")

    except Exception as e:
        print(f"[ERRO FATAL NO MAIN] Ocorreu um erro durante a execução principal: {e}")
    finally:
        print("[INFO] Fechando o crawler...")
        await crawler.close()
        print("[INFO] Processo finalizado.")


if __name__ == "__main__":
    asyncio.run(main())