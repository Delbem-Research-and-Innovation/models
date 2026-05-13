
import json
from Bio import Phylo
import networkx as nx
import os

def run_clustering(payload):
    """
    Função genérica que lê uma árvore de um ficheiro, processa a clusterização
    e gera um novo ficheiro com os resultados.
    """
    # 1. Extração de caminhos e parâmetros do payload
    # O código não tem nomes de ficheiros fixos, ele usa o que for enviado
    tree_path = payload.get('topology_tree_path')
    output_path = payload.get('output_file_path')
    tree_format = payload.get('tree_format', 'newick')
    algo_name = payload.get('clustering_strategy', {}).get('algorithm', 'fast_newman')

    # Validação de segurança
    if not tree_path or not os.path.exists(tree_path):
        return {"status": "error", "message": f"Arquivo de entrada não encontrado: {tree_path}"}

    # 2. Leitura do ficheiro de entrada (Qualquer .newick)
    try:
        tree = Phylo.read(tree_path, tree_format)
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler a árvore: {str(e)}"}

    # 3. Conversão para Grafo e Processamento Científico
    G = nx.Graph()
    for clade in tree.find_clades():
        for child in clade.clades:
            # Conecta nós para formar a rede complexa
            G.add_edge(str(clade.name), str(child.name))

    # Execução do algoritmo de comunidades (Gredy Modularity / Fast Newman)
    communities = list(nx.community.greedy_modularity_communities(G))
    q_score = nx.community.modularity(G, communities)

    # 4. Organização dos Dados (Filtra apenas as folhas/dados reais)
    leaves = [node.name for node in tree.get_terminals()]
    clusters_to_save = []
    
    for idx, comm in enumerate(communities):
        members = [str(node) for node in comm if node in leaves]
        if members:
            clusters_to_save.append({
                "cluster_id": idx,
                "elements": members
            })

    # 5. Geração do Ficheiro de Saída
    # Aqui o script "cospe" o resultado num novo arquivo físico
    with open(output_path, 'w') as f:
        json.dump({"clusters": clusters_to_save}, f, indent=4)

    # 6. Retorno do Contrato de Saída (Metadados)
    return {
        "status": "success",
        "topology_tree_path": tree_path,
        "clustering_algorithm": algo_name,
        "modularity_score_Q": round(q_score, 2),
        "total_clusters_detected": len(clusters_to_save),
        "output_file_path": output_path
    }

# --- BLOCO DE EXECUÇÃO PARA TESTES ---
# --- BLOCO DE EXECUÇÃO GENÉRICO ---
if __name__ == "__main__":
    import glob
    
    # Imprime a diretoria atual para confirmar onde o script está a procurar
    print(f"Diretoria de execução: {os.getcwd()}")

    # Procura por todos os ficheiros .newick
    arquivos_encontrados = glob.glob("*.newick")

    if not arquivos_encontrados:
        # Se não encontrar nada, lista o que existe na pasta para ajudar no diagnóstico
        print("Nenhum ficheiro .newick encontrado. Ficheiros na pasta:")
        print(os.listdir('.'))
    else:
        print(f"Sucesso: {len(arquivos_encontrados)} ficheiro(s) encontrado(s).\n")

        for ficheiro in arquivos_encontrados:
            payload_dinamico = {
                "topology_tree_path": ficheiro,
                "tree_format": "newick",
                "clustering_strategy": {"algorithm": "fast_newman"},
                "output_file_path": f"resultado_{ficheiro.replace('.newick', '.json')}"
            }

            print(f"--- A processar: {ficheiro} ---")
            resultado = run_clustering(payload_dinamico)
            
            # Exibe o resultado no terminal conforme solicitado
            print(json.dumps(resultado, indent=2))
            print(f"Saída salva em: {resultado['output_file_path']}\n")