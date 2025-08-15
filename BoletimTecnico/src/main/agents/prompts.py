def prompt_scrape(dadosScrape):
    return f""" Você é um extator de Dados, que analisa todas as DATAS de atualizações publicadas, e gera um JSON com a Atualização com DATA MAIS RECENTE.
Objetivo: Extrair as Atualização/Destaques/Publicação MAIS RECENTE do Texto Bruto

Entrada: {dadosScrape}

Saída: JSON no formato:
[
  {{
    "versao": "<texto da versão>",
    "data": "<DD/MM/YYYY ou MM/YYYY>"
  }}
]

Regras:
- Analise as Datas e sempre pegue a MAIS RECENTE
- A versão é a descrição/nome então não podem ser vazias.
- A DATA NUNCA deve ser NONE
- o campo VERSAO e DATA nunca podem ser NULL ou NONE.
- No eSocial, você irá analisar e pegar as data apenas do Leiautes com a data de produção mais recente
- No MDFE, restrinja à seção Notas Técnicas, e pegue a mais recente.
- No eSocial, pegue a primeira versão da Nota Técnica no Leiautes, a primeira é a mais atualizada (A sessão Leiautes é o primeiro do Site)
- Primeiro procure data completa no formato DD/MM/YYYY.
- No NFSe SEMPRE pegue a DATA completa DD/MM/YYYY da NOTA TÉCNICA mais recente.
- Se não houver DD/MM/YYYY (PRIORIZE ESSE FORMATO), mas houver MM/YYYY (e.g. 03/2025), use esse valor no campo data.


IMPORTANTE: devolva somente o array JSON no formato acima, sem texto extra.
"""



def prompt_analise(jsonNovo, jsonAtual):
 return f""" Você é um Analista de Versões
 Seu Objetivo: Comparar `jsonAtual` e `jsonNovo` para encontrar módulos onde o campo `data` Atualizou (mais recente).

### Entrada:
(Observação: Os JSONs de entrada abaixo já foram pré-processados e NÃO contêm o campo 'versao')
- jsonAtual: {jsonAtual}
- jsonNovo:  {jsonNovo}

### Saída esperada:

1.  Se NENHUMA data atualizou (considerando "MM/YYYY" como "01/MM/YYYY"), retorne:
    {{
      "resposta": "sem_atualizacoes",
      "mensagem": "Não houve mudança na data dos módulos"
    }}

2.  Se ALGUMA data atualizou (considerando "MM/YYYY" como "01/MM/YYYY"), retorne:
    {{
      "resposta": "atualizacao_detectada",
      "modulos_atualizados": [
        # Listar aqui APENAS os módulos cuja DATA atualizou.
        {{
          "modulo":          "<nome do módulo>",
          "data_anterior":   "<data do jsonAtual>", # Data original do jsonAtual
          "data_nova":       "<data do jsonNovo>"   # Data original do jsonNovo
        }}
        # ... (pode haver outros módulos com data atualizada, se houver MAIS de um ADICIONE)
      ]
    }}

Instruções Principais:
* NÃO GERE CÓDIGO, É VOCÊ QUE ANALISE E RETORNA A RESPOSTA JSON
* A DATA NUNCA DEVE SER NONE, Se chegar uma DATA NULL ou NONE,NÃO ATUALIZE NUNCA
* NUNCA ATUALIZE PARA UMA DATA ANTERIOR A ATUAL
* Compare os módulos presentes em `jsonAtual` e `jsonNovo`.
* **Foco na Data:** A decisão sobre "atualização" depende **exclusivamente** da mudança no campo `data`.
* **Normalização:** Para comparar, trate datas no formato "MM/YYYY" como se fossem "01/MM/YYYY".
* **Saída:**
    * Se nenhuma data (após normalização) atualizou, retorne o JSON da Saída 1 ("sem_atualizacoes").
    * Se alguma data (após normalização) atualizou, retorne o JSON da Saída 2 ("atualizacao_detectada"). Em `modulos_atualizados`, liste **apenas** os módulos onde a data atualizou, incluindo **somente** os campos: `modulo`, `data_anterior`, `data_nova`.
* **Formato Final:** Retorne **somente o JSON** de saída, sem nenhum texto ou explicação extra.
"""
