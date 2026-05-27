# Multimap Map Selector

Breve utilitário de recomendação de mapas temáticos (prova de conceito).

## Objetivo
Produzir especificações JSON de visualização (formato similar ao fixture de exemplo) a
partir de CSVs tabulares. O foco atual é gerar `choropleth` (mapa coroplético) quando
o dataset satisfaz critérios prudentes (coluna territorial + variável quantitativa
normalizável ou rate-like). O projeto também detecta outros tipos (heatmap,
proportional symbol, small multiples) e os reporta no terminal sem gerar JSONs
por padrão.

## Estrutura principal

- `src/multimap_map_selector/` — código fonte do pacote
  - `__init__.py` — API pública (`recommend_visualization_spec`) e composição
  - `profiling.py` — heurísticas de detecção de colunas, delimitador, flags
  - `rules.py` — regras determinísticas para selecionar tipo de mapa
  - `choropleth.py` — gerador de JSON no formato do fixture (com normalização opcional)
  - `gerador_de_bases_minimal.py` — gerador sintético de CSVs (stdlib-only)
  - `cli.py` — interface de linha de comando para processar um CSV ou diretório
  - `types.py` — dataclasses para `DatasetProfile`, `VisualizationSpec`, resultado

## Critérios para `choropleth`

Uma dataset é considerado para coropletico quando:

- contém uma chave territorial reconhecível (ex.: `cod_distr`, `distrito`, `geocode`)
- contém uma variável quantitativa adequada; preferimos em ordem:
  1. coluna rate-like (ex.: `taxa_*`, `*_perc`, `*_rate`) — mapeia diretamente
  2. coluna quantitativa + coluna de população → será normalizada (por 1000)
  3. exatamente uma variável quantitativa (é permitida mas o JSON inclui um aviso)

Se o dataset tem coordenadas ponto (`lat`/`lon`) e valores contínuos, a regra
prefere `heatmap` (não gera JSON choropleth). Se há múltiplas variáveis numéricas
com chave espacial, é sugerido `small_multiples`.

As decisões visam reduzir falsos-positivos: geramos JSON apenas quando as
condições acima indicam que um coropletico faz sentido segundo as práticas do
Desk Research (normalizar, limitar classes, incluir aviso sobre MAUP).

## Como usar (exemplos)

Do repositório raiz execute (forma simples, sem instalar pacote):

```bash
PYTHONPATH=models/multimap_map_selector/src \
  python3 -m multimap_map_selector.cli \
    --input models/multimap_map_selector \
    --output models/multimap_map_selector/test_results_batch \
    --batch
```

Para processar um único CSV:

```bash
PYTHONPATH=models/multimap_map_selector/src \
  python3 -m multimap_map_selector.cli --input path/to/file.csv --output outdir
```

Gerar datasets sintéticos (para testes):

```bash
python3 models/multimap_map_selector/src/multimap_map_selector/gerador_de_bases_minimal.py
```

Observações:
- O CLI imprime por arquivo se foi gerado um spec ou por que não foi (tipo e razão).
- Se não quiser exportar JSONs para tipos que não sejam `choropleth`, o código já
  exibe a razão em vez de criar ficheiros.

## Saída

Os specs são escritos como `visualization-spec-<id>.json` no diretório de saída.
O payload inclui `sources`, `layers`, `mapData`, `legends` e um `warnings` com
nota sobre agregação/MAUP quando apropriado.

## Como ajustar regras

- Editar heurísticas de colunas: `profiling.py` (tokens em `SPATIAL_KEYWORDS` e `NUMERIC_KEYWORDS`).
- Alterar prioridade/type matching: `rules.py`. As funções `_match_*` são pequenas
  e fáceis de modificar.
- Personalizar serialização/normalização: `choropleth.py` — a normalização por
  denominação está implementada e pode ser alterada (p.ex. per 10000).

## Boas práticas e advertências

- Choropleths devem mapear rates (não contagens brutas) sempre que possível.
- Incluímos um aviso de MAUP no JSON; recomendo revisar a normalização antes de
  publicar qualquer mapa.

## Próximos passos (opcionais)

- Tornar o pacote instalável (`pip install -e .`) para evitar `PYTHONPATH` hacks.
- Adicionar testes unitários cobrindo casos positivos/negativos das regras.
- Melhorar profiling com `pandas` para inferência robusta de tipos.

---
Se quiser, eu atualizo o README para adicionar exemplos de saída (trechos JSON)
ou criar um pequeno `Makefile` target para rodar o CLI com `PYTHONPATH` já
configurado.