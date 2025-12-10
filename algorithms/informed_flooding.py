"""
Implementação do algoritmo Informed Flooding (BFS com cache).
"""

from typing import Dict, List, Set, Tuple
from network import Network
from utils.cache import Cache


def informed_flooding(network: Network, start_node: str, resource: str, ttl: int = 10, cache: Cache = None) -> Dict:
    """
    Executa busca por informed flooding (BFS com cache).
    
    Args:
        network: Rede P2P
        start_node: Nó inicial da busca
        resource: Recurso a ser buscado
        ttl: Time to live (profundidade máxima)
        cache: Cache de recursos conhecidos
        
    Returns:
        Dicionário com resultados da busca
    """
    if cache is None:
        cache = Cache()
        cache.update_from_network(network)
    
    if start_node not in network.get_all_nodes():
        return {
            "found": False,
            "messages": 0,
            "nodes_visited": 0,
            "path": []
        }
    
    # Verificar cache do nó inicial
    if cache.has(start_node, resource):
        return {
            "found": True,
            "messages": 0,
            "nodes_visited": 1,
            "path": [start_node]
        }
    
    # Verificar se o nó inicial tem o recurso
    if network.has_resource(start_node, resource):
        cache.add(start_node, resource)
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
        
        # Filtrar vizinhos usando cache:
        # - Incluir nós que TÊM o recurso no cache (queremos visitá-los para confirmar)
        # - Incluir nós que NÃO estão no cache negativo (não sabemos se têm ou não)
        # - Excluir nós que sabemos que NÃO têm o recurso (cache negativo)
        neighbors = network.get_neighbors(current)
        filtered_neighbors = [
            n for n in neighbors 
            if cache.has(n, resource) or not cache.has_negative(n, resource)
        ]
        
        for neighbor in filtered_neighbors:
            messages += 1
            
            if neighbor not in visited:
                visited.add(neighbor)
                nodes_visited += 1
                new_path = path + [neighbor]
                
                # Verificar se encontrou o recurso
                if network.has_resource(neighbor, resource):
                    cache.add(neighbor, resource)
                    return {
                        "found": True,
                        "messages": messages,
                        "nodes_visited": nodes_visited,
                        "path": new_path
                    }
                else:
                    # Marcar no cache negativo que este nó não tem o recurso
                    cache.add_negative(neighbor, resource)
                
                # Adicionar à fila se ainda não atingiu TTL
                if depth + 1 < ttl:
                    queue.append((neighbor, depth + 1, new_path))
    
    return {
        "found": False,
        "messages": messages,
        "nodes_visited": nodes_visited,
        "path": list(visited)
    }

