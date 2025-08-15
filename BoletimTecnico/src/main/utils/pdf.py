from jinja2 import Environment, FileSystemLoader
import platform 
from weasyprint import HTML, CSS
from datetime import datetime
from config import PATHS

def gerar_boletim_pdf(dados):
    env = Environment(
        loader=FileSystemLoader(str(PATHS['template_dir'])),
        autoescape=True
    )  
    template = env.get_template('template.html')
    
    if platform.system() == "Windows":
        pathLogo = 'X:/BoletimTecnico/src/template/images/logo.png'
    else:
        pathLogo = str(PATHS['logo_path'])
        
    
    contexto = {
        'titulo_principal': 'Boletim de Atualização Técnica',
        'data': datetime.now().strftime('%d/%m/%Y'),
        'dados': dados,
        'logo_path': pathLogo
    }
    html = template.render(**contexto)
    HTML(string=html, base_url=str(PATHS['template_dir']) + '/') \
        .write_pdf(str(PATHS['pdf_output']),
                   stylesheets=[CSS(str(PATHS['template_css']))])
    print(f"PDF gerado em {PATHS['pdf_output']}")
