@echo off
setlocal EnableDelayedExpansion

REM ─── 1) Normaliza SCRIPT_DIR e ROOT ────────────────────
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\.."
set "ROOT=%CD%"

REM ─── 2) Garante que exista a pasta src\jsons ───────────
if not exist "%ROOT%\src\jsons" (
    mkdir "%ROOT%\src\jsons"
)

REM ─── 3) Copia jsonAtual.json da rede X (só na 1ª vez) ─
if not exist "%ROOT%\src\jsons\jsonAtual.json" (
    echo Copiando jsonAtual.json de X:\BoletimTecnico\jsons para src\jsons...
    copy "X:\BoletimTecnico\jsons\jsonAtual.json" "%ROOT%\src\jsons\jsonAtual.json"
)

REM ─── 4) Ativa o ambiente virtual ────────────────────────
call "%ROOT%\venv\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Falha ao ativar o venv.
    pause & exit /b 1
)

REM ─── 5) Instala navegadores Playwright ignorando SSL ───
set "NODE_TLS_REJECT_UNAUTHORIZED=0"
echo Instalando navegadores Playwright...
playwright install
set "NODE_TLS_REJECT_UNAUTHORIZED="

REM ─── 6) Carrega .env e configura Fontconfig no ambiente ─
if exist "%ROOT%\targetBoletim\.env" (
    echo Carregando variaveis de %ROOT%\targetBoletim\.env...
    for /f "usebackq tokens=1* delims== eol=#" %%A in ("%ROOT%\targetBoletim\.env") do (
        set "%%A=%%B"
    )
) else (
    echo [WARN] .env nao encontrado em %ROOT%\targetBoletim
)
set "FONTCONFIG_PATH=%ROOT%\targetBoletim\gtk3-runtime\etc\fonts"
set "FONTCONFIG_FILE=%ROOT%\targetBoletim\gtk3-runtime\etc\fonts\fonts.conf"

REM ─── 7) Muda para a pasta main para executar a aplicação ─────
cd /d "%ROOT%\src\main"

REM ─── 8) Executa a aplicação ─────────────────────────────
echo Iniciando aplicacao em %CD%...
python "app.py"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Erro durante a execucao da aplicacao.
) else (
    echo [OK] Execucao finalizada sem erros.
)

pause
endlocal
