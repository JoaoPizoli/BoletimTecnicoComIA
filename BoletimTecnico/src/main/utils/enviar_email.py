import os
import platform
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from config import PATHS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

dotenv_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(dotenv_path)

def enviar_email_com_anexo_pdf(assunto, corpo, destinatarios, caminho_anexo_pdf,
                               remetente="email@email.com", login_remetente="email@email.com"):
    """
    Envia um e-mail com um arquivo PDF em anexo.
    """
    senha = os.getenv("EMAIL_PASSWORD")
    if not senha:
        print("ERRO: Credenciais de e-mail (EMAIL_PASSWORD) não configuradas no arquivo .env!")
        return False

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = formataddr(('Boletim Técnico IA', remetente))
    msg['Sender'] = login_remetente
    msg['To'] = ", ".join(destinatarios)
    msg.set_content(corpo)

    if caminho_anexo_pdf and os.path.exists(caminho_anexo_pdf):
        try:
            with open(caminho_anexo_pdf, 'rb') as f:
                dados_pdf = f.read()
            nome_arquivo_pdf = os.path.basename(caminho_anexo_pdf)
            msg.add_attachment(dados_pdf, maintype='application', subtype='pdf', filename=nome_arquivo_pdf)
            print(f"INFO: Arquivo PDF '{nome_arquivo_pdf}' anexado com sucesso.")
        except Exception as e:
            print(f"ERRO: Falha ao anexar arquivo PDF '{caminho_anexo_pdf}': {e}")
    elif caminho_anexo_pdf:
        print(f"AVISO: Arquivo PDF para anexo não encontrado em '{caminho_anexo_pdf}'. O e-mail será enviado sem este anexo.")
    else:
        print("AVISO: Nenhum caminho de anexo PDF fornecido. O e-mail será enviado sem anexo.")


    try:
        with smtplib.SMTP("smtp.office365.com") as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(login_remetente, senha)
            smtp.send_message(msg)
        print(f"INFO: E-mail enviado com sucesso para: {', '.join(destinatarios)}!")
        return True
    except Exception as e:
        print(f"ERRO: Falha ao enviar e-mail: {e}")
        return False

def enviar_email_html(assunto, dados_html, destinatarios,
                   remetente="email@email.com", login_remetente="email@email.com",
                   anexar_pdf=False, caminho_anexo_pdf=None):
    """
    Envia um e-mail com conteúdo HTML direto no corpo da mensagem.

    Parâmetros:
    - assunto: Assunto do e-mail
    - dados_html: Um dicionário com os dados para renderizar o template HTML
    - destinatarios: Lista de e-mails dos destinatários
    - remetente: E-mail do remetente (exibido no campo From)
    - login_remetente: E-mail usado para autenticar no servidor SMTP
    - anexar_pdf: Se True, anexa também o PDF (para compatibilidade)
    - caminho_anexo_pdf: Caminho do arquivo PDF a ser anexado (se anexar_pdf for True)
    """
    senha = os.getenv("EMAIL_PASSWORD")
    if not senha:
        print("ERRO: Credenciais de e-mail (EMAIL_PASSWORD) não configuradas no arquivo .env!")
        return False# Configurar ambiente Jinja2
    env = Environment(
        loader=FileSystemLoader(str(PATHS['template_dir'])),
        autoescape=True
    )
    template = env.get_template('email_template.html')

    # Adicionar data atual ao contexto
    contexto = {
        'titulo_principal': 'Boletim de Atualização Técnica',
        'data': datetime.now().strftime('%d/%m/%Y'),
        'dados': dados_html
    }
    # Renderizar o HTML
    html_content = template.render(**contexto)

    # Criar mensagem
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = assunto
    msg_root['From'] = formataddr(('Boletim Técnico IA', remetente))
    msg_root['Sender'] = login_remetente
    msg_root['To'] = ", ".join(destinatarios)

    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    # Adicionar versão texto simples e HTML
    texto_simples = "Este e-mail contém conteúdo HTML. Por favor, use um cliente de e-mail que suporte HTML para visualizá-lo corretamente."
    msg_alternative.attach(MIMEText(texto_simples, 'plain'))
    msg_alternative.attach(MIMEText(html_content, 'html'))
    
    if platform.system() == "Windows":
        pathLogo = 'X:/BoletimTecnico/src/template/images/logo.png'
    else:
        pathLogo = PATHS['logo_path']
     
    logo_path = pathLogo
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as img_file:
                logo_data = img_file.read()
            logo_img = MIMEImage(logo_data)
            logo_img.add_header('Content-ID', '<logo@email.com>')  
            logo_img.add_header('Content-Disposition', 'inline', filename='logo.png')
            msg_root.attach(logo_img)
            print(f"INFO: Logo anexada com sucesso ao e-mail HTML.")
        except Exception as e:
            print(f"AVISO: Não foi possível anexar o logo ao e-mail: {e}")
    else:
        print(f"AVISO: Arquivo de logo não encontrado em {logo_path}. O e-mail será enviado sem o logo embutido.")

    # Anexar PDF se necessário
    if anexar_pdf and caminho_anexo_pdf and os.path.exists(caminho_anexo_pdf):
        try:
            with open(caminho_anexo_pdf, 'rb') as f:
                dados_pdf = f.read()
            nome_arquivo_pdf = os.path.basename(caminho_anexo_pdf)
            part = MIMEApplication(dados_pdf, Name=nome_arquivo_pdf)
            part['Content-Disposition'] = f'attachment; filename="{nome_arquivo_pdf}"'
            msg_root.attach(part)
            print(f"INFO: Arquivo PDF '{nome_arquivo_pdf}' anexado com sucesso.")
        except Exception as e:
            print(f"ERRO: Falha ao anexar arquivo PDF '{caminho_anexo_pdf}': {e}")

    # Enviar e-mail
    try:
        with smtplib.SMTP("smtp.office365.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(login_remetente, senha)
            smtp.send_message(msg_root)
        print(f"INFO: E-mail HTML enviado com sucesso para: {', '.join(destinatarios)}!")
        return True
    except Exception as e:
        print(f"ERRO: Falha ao enviar e-mail HTML: {e}")
        return False
