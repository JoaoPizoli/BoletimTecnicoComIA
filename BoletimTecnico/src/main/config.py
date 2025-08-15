import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import os
import platform
from pathlib import Path


# Diretório base do projeto (pai de src)
BASE_DIR = Path(__file__).resolve().parents[1]

# Configuração de caminhos dinâmicos
def get_project_paths():
    """
    Retorna os caminhos dinâmicos do projeto usando referências relativas.
    """
    # Diretório atual do script (BoletimTecnico/src/main)
    current_dir = Path(__file__).resolve().parent
    
    # Navegar para o diretório raiz do Boletim (trunk/Boletim)
    boletim_root = current_dir.parents[2]  # Volta 3 níveis: main -> src -> BoletimTecnico -> Boletim
    
    # Definir caminho dos JSONs baseado no sistema operacional
    if platform.system() == "Windows":
        # No Windows, usa src/jsons
        json_base_dir = current_dir.parent / 'jsons'
    else:
        # Em outros sistemas, mantém o caminho original
        json_base_dir = Path('/dados/BoletimTecnico')
    
    paths = {
        # Caminhos para JSONs - dependente do SO
        'json_dir': json_base_dir,
        'json_atual': json_base_dir / 'jsonAtual.json',
        'json_novo': json_base_dir / 'jsonNovo.json',
        'json_analise': json_base_dir / 'analise.json',
        
        # Caminhos para templates (relativos ao projeto)
        'template_dir': current_dir / 'template',
        'template_html': current_dir / 'template' / 'template.html',
        'template_email': current_dir / 'template' / 'email_template.html',
        'template_css': current_dir / 'template' / 'styles.css',
        
        # Caminho para o logo (Template/Images/logo.png)
        'logo_path': boletim_root / 'Template' / 'Images' / 'logo.png',
        
        # Diretório de saída para PDFs
        'output_dir': boletim_root / 'BoletimTecnico' / 'target' / 'outputs',
        'pdf_output': boletim_root / 'BoletimTecnico' / 'target' / 'outputs' / 'boletim_tecnico.pdf',
        
        # Diretório base do projeto
        'project_root': current_dir,
        'boletim_root': boletim_root
    }
    
    # Criar diretórios necessários
    paths['json_dir'].mkdir(parents=True, exist_ok=True)
    paths['output_dir'].mkdir(parents=True, exist_ok=True)
    
    return paths

# Inicializar caminhos
PATHS = get_project_paths()

# Configurações específicas para Ubuntu/Linux
if platform.system() == "Linux":
    print("[INFO] Sistema detectado: Linux/Ubuntu")
    print("[INFO] Carregando variáveis de ambiente do sistema...")
    
    required_env_vars = [
        "EMAIL_FROM", "EMAIL_PASSWORD", "EMAIL_TO", 
        "OPENAI_API_KEY_BOLETIM", "OPENAI_MODEL"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERRO] As seguintes variáveis de ambiente não estão definidas no sistema: {', '.join(missing_vars)}")
        print("[INFO] Certifique-se de exportar essas variáveis no Ubuntu antes de executar o script.")
        print("[INFO] Exemplo: export EMAIL_FROM='seu@email.com'")
        raise EnvironmentError(f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}")
    
    print("[INFO] Todas as variáveis de ambiente necessárias foram encontradas no sistema.")
    
# Configuração para Windows
elif platform.system() == "Windows":
    print("[INFO] Sistema detectado: Windows")
    print("[INFO] Configurando ambiente Windows...")
    
    from dotenv import load_dotenv
    
    env_path = BASE_DIR / ".." / "targetBoletim" / ".env"
    if not env_path.is_file():
        raise FileNotFoundError(f".env não encontrado em {env_path}")
    load_dotenv(dotenv_path=env_path)
    print(f"[INFO] Variáveis carregadas do arquivo {env_path}")
    
    # 2) Configura DLLs do GTK para WeasyPrint (Windows)
    gtk_root = BASE_DIR / ".." / "targetBoletim" / "gtk3-runtime"
    if not gtk_root.is_dir():
        raise FileNotFoundError(f"gtk3-runtime não encontrado em {gtk_root}")
    
    # Procura pela DLL principal ou todas as DLLs
    dll_paths = list(gtk_root.rglob("libgobject-2.0-0.dll"))
    if dll_paths:
        os.add_dll_directory(str(dll_paths[0].parent))
        print(f"[INFO] DLL principal encontrada em {dll_paths[0].parent}")
    else:
        all_dlls = list(gtk_root.rglob("*.dll"))
        if not all_dlls:
            raise FileNotFoundError(f"Nenhuma DLL encontrada em {gtk_root}")
        for dll_dir in {p.parent for p in all_dlls}:
            os.add_dll_directory(str(dll_dir))
        print(f"[INFO] {len(all_dlls)} DLLs configuradas")
    
    # 3) Configuração do Fontconfig
    font_dir = gtk_root / "etc" / "fonts"
    if not font_dir.is_dir():
        raise FileNotFoundError(f"Pasta de fonts não encontrada em {font_dir}")
    
    os.environ["FONTCONFIG_PATH"] = str(font_dir)
    os.environ["FONTCONFIG_FILE"] = str(font_dir / "fonts.conf")
    print(f"[INFO] Fontconfig configurado em {font_dir}")

else:
    # Outros sistemas operacionais
    print(f"[AVISO] Sistema detectado: {platform.system()}")
    print("[AVISO] Este código foi otimizado para Ubuntu/Linux e Windows")
    print("[INFO] Tentando usar variáveis do sistema operacional...")