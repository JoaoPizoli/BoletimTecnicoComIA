# Boletim Técnico IA

Sistema automatizado para monitoramento e notificação de atualizações em módulos fiscais e documentos técnicos relevantes.

![Logo Metalúrgica Mococa](./template/images/logo.png)

## 📋 Descrição

O Boletim Técnico IA é uma ferramenta de automação que monitora atualizações em diversos módulos fiscais e técnicos (como CTe, NFe, ECD, NFCe, entre outros) relevantes para operações fiscais e contábeis. O sistema realiza web scraping nas fontes oficiais, identifica atualizações, gera relatórios em PDF e envia notificações por e-mail.

## 🚀 Funcionalidades

- **Web Scraping Inteligente**: Coleta dados de múltiplas fontes oficiais de documentos técnicos e fiscais
- **Análise Automática**: Compara datas e versões para detectar atualizações
- **Relatórios em PDF**: Gera boletins técnicos em formato PDF para documentação e distribuição
- **Notificações por E-mail**: Envia e-mails formatados em HTML com resumo das atualizações e PDF anexo
- **Integração com IA**: Utiliza GPT-4o-mini para análise e formatação de dados

## 🔍 Módulos Monitorados

- CTE (Conhecimento de Transporte Eletrônico)
- ECD (Escrituração Contábil Digital)
- ECF (Escrituração Contábil Fiscal)
- EFD CONTRIBUIÇÕES
- EFD ICMS IPI
- EFD REINF
- ESOCIAL
- MDFE (Manifesto Eletrônico de Documentos Fiscais)
- NFCE (Nota Fiscal de Consumidor Eletrônica)
- NFE (Nota Fiscal Eletrônica)
- NFSE (Nota Fiscal de Serviços Eletrônica)

## 🧩 Estrutura do Projeto

```
├── app.py                  # Ponto de entrada principal da aplicação
├── agents/                 # Agentes de IA para processamento de dados
│   ├── agentes.py          # Implementação dos agentes de IA
│   ├── prompts.py          # Prompts utilizados pelos agentes
├── jsons/                  # Arquivos JSON para armazenamento de dados
│   ├── analise.json        # Resultado da análise comparativa
│   ├── jsonAtual.json      # Dados atuais dos módulos
│   ├── jsonNovo.json       # Novos dados obtidos pelo scraping
├── output/                 # Diretório para armazenamento dos PDFs gerados
├── template/               # Templates HTML para PDF e e-mail
│   ├── email_template.html # Template HTML para e-mail
│   ├── styles.css          # Estilos CSS para o PDF
│   ├── template.html       # Template HTML para o PDF
│   ├── images/
│       ├── logo.png        # Logo da empresa
├── utils/                  # Utilitários
│   ├── enviar_email.py     # Funções para envio de e-mails
│   ├── pdf.py              # Funções para geração de PDFs
│   ├── scrape.py           # Funções para web scraping
```

## ⚙️ Requisitos

- Python 3.10+
- Bibliotecas principais:
  - openai
  - jinja2
  - weasyprint
  - aiofiles
  - asyncio
  - crawl4ai
  - dotenv

## 🔧 Configuração

1. Instale as dependências:
```bash
pip install openai jinja2 weasyprint aiofiles crawl4ai python-dotenv
```

2. Configure o arquivo `.env` na raiz do projeto com suas credenciais:
```
EMAIL_PASSWORD=sua_senha_email
OPENAI_API_KEY=sua_chave_api_openai
```

3. Verifique e atualize as URLs de scraping no arquivo `utils/scrape.py` conforme necessário.

## 🚀 Execução

Para executar o sistema completo:

```bash
python app.py
```

O processo irá:
1. Realizar o scraping das fontes definidas
2. Analisar os dados obtidos para identificar atualizações
3. Gerar um PDF com as informações de atualização (se houver)
4. Enviar e-mail com o relatório para os destinatários configurados

## 📧 Envio de E-mail

O sistema possui dois métodos de envio de e-mail:
- **E-mail HTML**: Mais visual, com tabela formatada e logo da empresa
- **E-mail com Anexo PDF**: Método de fallback caso o HTML falhe

Os destinatários podem ser configurados no arquivo `app.py`.

## 🤖 Agentes IA

O sistema utiliza dois agentes de IA baseados no modelo GPT-4o-mini:

- **Agente_Formatador**: Processa os dados brutos do scraping e os formata em JSON estruturado
- **Agente_Analisador**: Compara os dados novos e atuais para detectar atualizações

## 🔄 Fluxo de Processamento

1. **Coleta de Dados**:
   - O sistema faz web scraping das fontes oficiais configuradas
   - Os dados são processados pelo Agente_Formatador para estruturação

2. **Análise Comparativa**:
   - Os dados novos são comparados com os dados armazenados anteriormente
   - O Agente_Analisador identifica módulos que foram atualizados

3. **Geração de Relatório**:
   - Se houver atualizações, um relatório PDF é gerado com os detalhes
   - O relatório inclui: módulo, data anterior, data nova, versão e link para a fonte

4. **Notificação**:
   - Um e-mail é enviado aos destinatários configurados
   - O e-mail contém um resumo das atualizações e o PDF anexado

## 🧑‍💻 Desenvolvimento

Desenvolvido por **João Pedro Pizoli Carvalho**
