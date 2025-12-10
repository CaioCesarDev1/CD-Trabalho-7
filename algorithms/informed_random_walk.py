"""
Implementação do algoritmo Informed Random Walk (com cache).
"""

from typing import Dict, List, Set, Tuple
import random
from network import Network
from utils.cache import Cache


def informed_random_walk(network: Network, start_node: str, resource: str, ttl: int = 10, cache: Cache = None) -> Dict:
    """
    Executa busca por informed random walk (com cache).
    
    Args:
        network: Rede P2P
        start_node: Nó inicial da busca
        resource: Recurso a ser buscado
        ttl: Time to live (número máximo de passos)
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
    
    current = start_node
    path = [start_node]
    visited = {start_node}
    messages = 0
    steps = 0
    
    while steps < ttl:
        neighbors = list(network.get_neighbors(current))
        
        if not neighbors:
            break
        
        # Filtrar vizinhos usando cache:
        # - Incluir nós que TÊM o recurso no cache
        # - Incluir nós que NÃO estão no cache negativo
        # - Excluir nós que sabemos que NÃO têm o recurso
        candidate_neighbors = [
            n for n in neighbors 
            if cache.has(n, resource) or not cache.has_negative(n, resource)
        ]
        
        if not candidate_neighbors:
            # Se todos têm cache negativo, escolher aleatoriamente (fallback)
            candidate_neighbors = neighbors
        
        # Escolher vizinho aleatório dos candidatos
        next_node = random.choice(candidate_neighbors)
        messages += 1
        steps += 1
        
        if next_node not in visited:
            visited.add(next_node)
        
        path.append(next_node)
        current = next_node
        
        # Verificar se encontrou o recurso
        if network.has_resource(current, resource):
            cache.add(current, resource)
            return {
                "found": True,
                "messages": messages,
                "nodes_visited": len(visited),
                "path": path
            }
        else:
            # Marcar no cache negativo que este nó não tem o recurso
            cache.add_negative(current, resource)
    
    return {
        "found": False,
        "messages": messages,
        "nodes_visited": len(visited),
        "path": path
    }

