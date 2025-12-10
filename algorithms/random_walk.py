"""
Implementação do algoritmo Random Walk.
"""

from typing import Dict, List, Set, Tuple
import random
from network import Network


def random_walk(network: Network, start_node: str, resource: str, ttl: int = 10) -> Dict:
    """
    Executa busca por random walk.
    
    Args:
        network: Rede P2P
        start_node: Nó inicial da busca
        resource: Recurso a ser buscado
        ttl: Time to live (número máximo de passos)
        
    Returns:
        Dicionário com resultados da busca
    """
    if start_node not in network.get_all_nodes():
        return {
            "found": False,
            "messages": 0,
            "nodes_visited": 0,
            "path": []
        }
    
    # Verificar se o nó inicial tem o recurso
    if network.has_resource(start_node, resource):
        return {
            "found": True,
            "messages": 0,
            "nodes_visited": 1,
            "path": [start_node]
        }
    
    current = start_node
    path = [start_node]
    visited = {start_node}
    messages = 0
    steps = 0
    
    while steps < ttl:
        neighbors = list(network.get_neighbors(current))
        
        if not neighbors:
            break
        
        # Escolher vizinho aleatório
        next_node = random.choice(neighbors)
        messages += 1
        steps += 1
        
        if next_node not in visited:
            visited.add(next_node)
        
        path.append(next_node)
        current = next_node
        
        # Verificar se encontrou o recurso
        if network.has_resource(current, resource):
            return {
                "found": True,
                "messages": messages,
                "nodes_visited": len(visited),
                "path": path
            }
    
    return {
        "found": False,
        "messages": messages,
        "nodes_visited": len(visited),
        "path": path
    }

