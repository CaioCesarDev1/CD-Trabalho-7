"""
Módulo para visualização gráfica da rede usando networkx e matplotlib.
"""

import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para evitar problemas em servidores
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Set, Optional
from network import Network


def draw_network(network: Network, 
                 highlight_node: Optional[str] = None,
                 highlight_path: Optional[List[str]] = None,
                 title: str = "Rede P2P",
                 output_file: Optional[str] = None,
                 show_labels: bool = True):
    """
    Desenha a rede P2P com destaque para nó e caminho.
    
    Args:
        network: Rede P2P
        highlight_node: Nó a ser destacado (ex: nó que tem o recurso)
        highlight_path: Caminho percorrido pelo algoritmo
        title: Título do gráfico
        output_file: Arquivo para salvar (None = mostrar na tela)
        show_labels: Se True, mostra labels dos nós
    """
    G = nx.Graph()
    
    # Adicionar nós e arestas
    for node in network.get_all_nodes():
        G.add_node(node)
    
    for edge in network.edges:
        G.add_edge(edge[0], edge[1])
    
    # Layout
    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
    
    # Configurar figura
    plt.figure(figsize=(14, 10))
    
    # Desenhar arestas normais
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='gray', width=1.5)
    
    # Desenhar arestas do caminho destacado
    if highlight_path and len(highlight_path) > 1:
        path_edges = [(highlight_path[i], highlight_path[i+1]) 
                     for i in range(len(highlight_path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                              edge_color='red', width=3, alpha=0.7, style='dashed')
    
    # Desenhar nós normais
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node == highlight_node:
            node_colors.append('red')
            node_sizes.append(800)
        elif highlight_path and node in highlight_path:
            node_colors.append('orange')
            node_sizes.append(600)
        else:
            node_colors.append('lightblue')
            node_sizes.append(400)
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.8)
    
    # Labels dos nós com recursos
    if show_labels:
        labels = {}
        for node in G.nodes():
            resources = network.resources.get(node, [])
            if resources:
                labels[node] = f"{node}\n{', '.join(resources)}"
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo em: {output_file}")
    else:
        # Se não houver output_file, criar um nome padrão
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        default_file = f"network_{safe_title}.png"
        plt.savefig(default_file, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo em: {default_file}")
    
    plt.close()

