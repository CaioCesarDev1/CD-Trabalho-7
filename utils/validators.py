"""
Módulo de validação da topologia da rede.
"""

from typing import Dict, List, Tuple
import sys
import os

# Adicionar diretório raiz ao path para importar network
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from network import Network


class ValidationError(Exception):
    """Exceção para erros de validação."""
    pass


def validate_network(config: Dict) -> Tuple[bool, List[str]]:
    """
    Valida a configuração da rede.
    
    Args:
        config: Dicionário com configuração da rede
        
    Returns:
        Tupla (is_valid, errors)
    """
    errors = []
    
    # Verificar campos obrigatórios
    required_fields = ['num_nodes', 'min_neighbors', 'max_neighbors', 'resources', 'edges']
    for field in required_fields:
        if field not in config:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    if errors:
        return False, errors
    
    num_nodes = config['num_nodes']
    min_neighbors = config['min_neighbors']
    max_neighbors = config['max_neighbors']
    resources = config['resources']
    edges = config['edges']
    
    # Validar número de nós
    if num_nodes != len(resources):
        errors.append(f"num_nodes ({num_nodes}) não corresponde ao número de nós em resources ({len(resources)})")
    
    # Validar que todos os nós têm recursos
    for node, node_resources in resources.items():
        if not node_resources:
            errors.append(f"Nó {node} não possui recursos")
    
    # Validar arestas
    all_nodes = set(resources.keys())
    for edge in edges:
        if len(edge) != 2:
            errors.append(f"Aresta inválida: {edge}")
            continue
        
        node1, node2 = edge
        if node1 == node2:
            errors.append(f"Aresta inválida (self-loop): {node1} -> {node2}")
        
        if node1 not in all_nodes:
            errors.append(f"Nó {node1} não existe em resources")
        
        if node2 not in all_nodes:
            errors.append(f"Nó {node2} não existe em resources")
    
    # Criar rede temporária para validações de grafo
    try:
        network = Network(num_nodes, resources, edges)
        
        # Validar conectividade
        if not network.is_connected():
            errors.append("A rede não é conectada")
        
        # Validar graus
        for node in all_nodes:
            degree = network.get_degree(node)
            if degree < min_neighbors:
                errors.append(f"Nó {node} tem {degree} vizinhos, mas mínimo é {min_neighbors}")
            if degree > max_neighbors:
                errors.append(f"Nó {node} tem {degree} vizinhos, mas máximo é {max_neighbors}")
    
    except Exception as e:
        errors.append(f"Erro ao criar rede: {str(e)}")
    
    return len(errors) == 0, errors

