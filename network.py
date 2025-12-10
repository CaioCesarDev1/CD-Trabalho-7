"""
Módulo que representa a estrutura da rede P2P.
Gerencia nós, arestas, recursos e cache.
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict


class Network:
    """Representa uma rede P2P não estruturada."""
    
    def __init__(self, num_nodes: int, resources: Dict[str, List[str]], edges: List[List[str]]):
        """
        Inicializa a rede.
        
        Args:
            num_nodes: Número total de nós
            resources: Dicionário {node_id: [resource_ids]}
            edges: Lista de arestas [[node1, node2], ...]
        """
        self.num_nodes = num_nodes
        self.resources = resources
        self.edges = edges
        
        # Construir grafo de adjacência
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        for node1, node2 in edges:
            self.graph[node1].add(node2)
            self.graph[node2].add(node1)
        
        # Garantir que todos os nós existam no grafo (mesmo sem arestas)
        for node in resources.keys():
            if node not in self.graph:
                self.graph[node] = set()
        
        # Cache para algoritmos informados (armazena recursos encontrados por nó)
        self.cache: Dict[str, Set[str]] = defaultdict(set)
    
    def get_neighbors(self, node: str) -> Set[str]:
        """Retorna os vizinhos de um nó."""
        return self.graph.get(node, set())
    
    def get_degree(self, node: str) -> int:
        """Retorna o grau (número de vizinhos) de um nó."""
        return len(self.get_neighbors(node))
    
    def has_resource(self, node: str, resource: str) -> bool:
        """Verifica se um nó possui um recurso."""
        return resource in self.resources.get(node, [])
    
    def get_all_nodes(self) -> Set[str]:
        """Retorna todos os nós da rede."""
        return set(self.resources.keys())
    
    def add_to_cache(self, node: str, resource: str):
        """Adiciona um recurso ao cache de um nó."""
        self.cache[node].add(resource)
    
    def get_cache(self, node: str) -> Set[str]:
        """Retorna o cache de um nó."""
        return self.cache.get(node, set())
    
    def clear_cache(self):
        """Limpa todo o cache."""
        self.cache.clear()
    
    def is_connected(self) -> bool:
        """Verifica se a rede é conectada usando BFS."""
        nodes = self.get_all_nodes()
        if not nodes:
            return True
        
        start = next(iter(nodes))
        visited = set()
        queue = [start]
        visited.add(start)
        
        while queue:
            current = queue.pop(0)
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(nodes)

