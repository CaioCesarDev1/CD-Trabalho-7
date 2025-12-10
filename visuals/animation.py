"""
Módulo para animação da busca na rede.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
from typing import List, Optional
from network import Network


def animate_search(network: Network,
                   path: List[str],
                   resource: str,
                   title: str = "Animação da Busca",
                   interval: int = 500,
                   output_file: Optional[str] = None):
    """
    Cria animação mostrando o caminho da busca.
    
    Args:
        network: Rede P2P
        path: Caminho percorrido
        resource: Recurso buscado
        title: Título da animação
        interval: Intervalo entre frames (ms)
        output_file: Arquivo para salvar (None = mostrar na tela)
    """
    G = nx.Graph()
    
    # Adicionar nós e arestas
    for node in network.get_all_nodes():
        G.add_node(node)
    
    for edge in network.edges:
        G.add_edge(edge[0], edge[1])
    
    # Layout fixo
    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Desenhar estrutura base
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color='gray', width=1.5)
    
    # Labels
    labels = {}
    for node in G.nodes():
        resources = network.resources.get(node, [])
        if resources:
            labels[node] = f"{node}\n{', '.join(resources)}"
        else:
            labels[node] = node
    
    def update(frame):
        ax.clear()
        ax.set_title(f"{title} - Passo {frame + 1}/{len(path)}", 
                    fontsize=14, fontweight='bold')
        
        # Desenhar arestas
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color='gray', width=1.5)
        
        # Desenhar caminho até o frame atual
        if frame > 0:
            path_edges = [(path[i], path[i+1]) for i in range(frame)]
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, ax=ax,
                                  edge_color='red', width=3, alpha=0.7, style='dashed')
        
        # Cores dos nós
        node_colors = []
        node_sizes = []
        current_node = path[frame] if frame < len(path) else None
        
        for node in G.nodes():
            if node == current_node:
                node_colors.append('red')
                node_sizes.append(800)
            elif node in path[:frame+1]:
                node_colors.append('orange')
                node_sizes.append(600)
            else:
                node_colors.append('lightblue')
                node_sizes.append(400)
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, ax=ax, alpha=0.8)
        nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=8, font_weight='bold')
        
        ax.axis('off')
    
    anim = animation.FuncAnimation(fig, update, frames=len(path), 
                                  interval=interval, repeat=True)
    
    if output_file:
        anim.save(output_file, writer='pillow', fps=2)
        print(f"Animação salva em: {output_file}")
    else:
        plt.show()
    
    return anim

