"""
Módulo de cache para algoritmos informados.
"""

from typing import Dict, Set


class Cache:
    """Gerencia cache de recursos encontrados."""
    
    def __init__(self):
        """Inicializa o cache vazio."""
        self.cache: Dict[str, Set[str]] = {}  # Recursos que os nós TÊM
        self.negative_cache: Dict[str, Set[str]] = {}  # Recursos que os nós NÃO têm
    
    def add(self, node: str, resource: str):
        """Adiciona um recurso ao cache de um nó (recurso positivo)."""
        if node not in self.cache:
            self.cache[node] = set()
        self.cache[node].add(resource)
        # Remover de negative_cache se estiver lá
        if node in self.negative_cache:
            self.negative_cache[node].discard(resource)
    
    def add_negative(self, node: str, resource: str):
        """Adiciona informação negativa: nó NÃO tem o recurso."""
        if node not in self.negative_cache:
            self.negative_cache[node] = set()
        self.negative_cache[node].add(resource)
    
    def has(self, node: str, resource: str) -> bool:
        """Verifica se um nó tem um recurso em cache (positivo)."""
        return resource in self.cache.get(node, set())
    
    def has_negative(self, node: str, resource: str) -> bool:
        """Verifica se sabemos que um nó NÃO tem o recurso."""
        return resource in self.negative_cache.get(node, set())
    
    def get(self, node: str) -> Set[str]:
        """Retorna todos os recursos em cache de um nó (positivos)."""
        return self.cache.get(node, set())
    
    def clear(self):
        """Limpa todo o cache."""
        self.cache.clear()
        self.negative_cache.clear()
    
    def update_from_network(self, network):
        """Atualiza o cache com os recursos reais da rede."""
        for node, resources in network.resources.items():
            for resource in resources:
                self.add(node, resource)

