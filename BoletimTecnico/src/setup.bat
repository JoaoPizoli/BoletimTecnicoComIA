:: src\setup.bat
@echo off
setlocal

REM ─── Determina pastas ────────────────────────────────
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%..\"

REM ─── Vai para a raiz do projeto ──────────────────────
cd /d "%ROOT%"

REM ─── Etapa 1: Sincroniza a pasta "target" da rede ────
echo Iniciando sincronizacao da pasta "targetBoletim"...
robocopy "X:\BoletimTecnico\targetBoletim" "%ROOT%targetBoletim" /MIR /Z /COPY:DAT /R:3 /W:5 /ETA
if errorlevel 8 (
    echo [ERROR] Falha ao sincronizar target.
    pause
    exit /b 1
)
echo [OK] target sincronizado.
echo ==============================================

REM ─── Etapa 2: Variáveis de ambiente ─────────────────
set "GTK3_DLL_DIR=%ROOT%targetBoletim\gtk3-runtime\$_63_\bin"
set "FONTCONFIG_PATH=%ROOT%targetBoletim\gtk3-runtime\etc\fonts"
set "FONTCONFIG_FILE=%ROOT%targetBoletim\gtk3-runtime\etc\fonts\fonts.conf"
echo [OK] Variáveis definidas.

REM ─── Etapa 3: Cria/atualiza venv e instala deps ──────
if not exist "%ROOT%venv\" (
    echo Criando venv...
    "%ROOT%targetBoletim\Python313\python.exe" -m venv "%ROOT%venv"
    if errorlevel 1 (
        echo [ERROR] Nao foi possivel criar venv.
        pause
        exit /b 1
    )
)
echo Ativando venv e instalando dependências...
call "%ROOT%venv\Scripts\activate.bat"
python -m pip install --upgrade pip

REM ===== LINHAS DE DEBUG ADICIONADAS AQUI =====
echo [DEBUG] Current Directory (apos ativar venv): %CD%
echo [DEBUG] ROOT variable is: %ROOT%
echo [DEBUG] Caminho completo para requirements.txt que sera usado: "%ROOT%targetBoletim\requirements.txt"
echo [DEBUG] Verificando se o arquivo existe no local acima (com dir):
dir "%ROOT%targetBoletim\requirements.txt"
echo [DEBUG] Conteudo do arquivo requirements.txt:
type "%ROOT%targetBoletim\requirements.txt"
pause
REM ===== FIM DAS LINHAS DE DEBUG =====

pip install -r "%ROOT%targetBoletim\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Falha na instalacao das dependencias.
    pause
    exit /b 1
)
echo [OK] Setup concluido.
pause
endlocal