# Column Matcher Similarity Analysis

## Intent
Identificar pares de colunas entre dois esquemas de dados diferentes que possuam similaridade semântica ou sintática, facilitando o mapeamento automático de tabelas.

## Inputs
- source_columns: Lista de strings contendo os nomes das colunas da tabela de origem.
- target_columns: Lista de strings contendo os nomes das colunas da tabela de destino.
- similarity_threshold: Float entre 0.0 e 1.0 (padrão 0.8) que define o limite mínimo para considerar um "match".

## Output
Uma lista de dicionários (ou tuplas) contendo:
- source: Nome da coluna de origem.
- target: Nome da coluna de destino.
- score: Grau de similaridade (float).

## Business rules
1. A comparação deve ser case-insensitive (ignorar maiúsculas/minúsculas).
2. Se houver um "match" exato (100%), ele deve ser priorizado e retornado imediatamente.
3. Utilizar algoritmos de distância de edição (como Levenshtein via library thefuzz ou difflib).
4. Se o similarity_threshold for inválido (fora de 0-1), deve gerar um ValueError.
5. Retornar apenas os pares que atingirem ou superarem o threshold.

## Acceptance criteria
- Implementação seguindo estritamente o paradigma funcional (sem classes).
- Uso de funções puras e modulares.
- Cobertura de testes para matches exatos, matches parciais e nenhum match.
- Performance aceitável para listas de até 500 colunas.

## Non-goals
- Não deve realizar análise do conteúdo das colunas (apenas dos nomes/metadados).
- Não deve realizar tradução automática de idiomas.
