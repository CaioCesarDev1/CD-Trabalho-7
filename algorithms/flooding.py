"""
Implementação do algoritmo Flooding (BFS).
"""

from typing import Dict, List, Set, Tuple
from network import Network


def flooding(network: Network, start_node: str, resource: str, ttl: int = 10) -> Dict:
    """
    Executa busca por flooding (BFS).
    
    Args:
        network: Rede P2P
        start_node: Nó inicial da busca
        resource: Recurso a ser buscado
        ttl: Time to live (profundidade máxima)
        
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
    
    visited = set()
    queue = [(start_node, 0, [start_node])]  # (node, depth, path)
    visited.add(start_node)
    messages = 0
    nodes_visited = 1
    
    while queue:
        current, depth, path = queue.pop(0)
        
        if depth >= ttl:
            continue
        
        # Enviar mensagem para todos os vizinhos
        neighbors = network.get_neighbors(current)
        for neighbor in neighbors:
            messages += 1
            
            if neighbor not in visited:
                visited.add(neighbor)
                nodes_visited += 1
                new_path = path + [neighbor]
                
                # Verificar se encontrou o recurso
                if network.has_resource(neighbor, resource):
                    return {
                        "found": True,
                        "messages": messages,
                        "nodes_visited": nodes_visited,
                        "path": new_path,
                        "all_visited": list(visited)  # Todos os nós visitados
                    }
                
                # Adicionar à fila se ainda não atingiu TTL
                if depth + 1 < ttl:
                    queue.append((neighbor, depth + 1, new_path))
    
    return {
        "found": False,
        "messages": messages,
        "nodes_visited": nodes_visited,
        "path": list(visited),
        "all_visited": list(visited)  # Todos os nós visitados
    }

