"""
Módulo para métricas e gráficos de desempenho.
"""

from typing import Dict, List
import matplotlib.pyplot as plt
import pandas as pd


def create_performance_chart(results: Dict[str, Dict], output_file: str = "performance.png"):
    """
    Cria gráfico comparativo de desempenho dos algoritmos.
    
    Args:
        results: Dicionário {algorithm_name: {messages, nodes_visited, found}}
        output_file: Nome do arquivo de saída
    """
    algorithms = list(results.keys())
    messages = [results[alg]["messages"] for alg in algorithms]
    nodes_visited = [results[alg]["nodes_visited"] for alg in algorithms]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico de mensagens
    ax1.bar(algorithms, messages, color='skyblue', edgecolor='navy', alpha=0.7)
    ax1.set_xlabel('Algoritmo', fontsize=12)
    ax1.set_ylabel('Mensagens Enviadas', fontsize=12)
    ax1.set_title('Comparação de Mensagens Enviadas', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for i, v in enumerate(messages):
        ax1.text(i, v + max(messages) * 0.01, str(v), ha='center', va='bottom')
    
    # Gráfico de nós visitados
    ax2.bar(algorithms, nodes_visited, color='lightcoral', edgecolor='darkred', alpha=0.7)
    ax2.set_xlabel('Algoritmo', fontsize=12)
    ax2.set_ylabel('Nós Visitados', fontsize=12)
    ax2.set_title('Comparação de Nós Visitados', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for i, v in enumerate(nodes_visited):
        ax2.text(i, v + max(nodes_visited) * 0.01, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo em: {output_file}")


def create_ttl_comparison_chart(ttl_results: Dict[int, Dict[str, Dict]], output_file: str = "ttl_comparison.png"):
    """
    Cria gráfico comparando taxa de sucesso vs TTL.
    
    Args:
        ttl_results: Dicionário {ttl: {algorithm: {found, messages, nodes_visited}}}
        output_file: Nome do arquivo de saída
    """
    ttls = sorted(ttl_results.keys())
    algorithms = set()
    for ttl_data in ttl_results.values():
        algorithms.update(ttl_data.keys())
    algorithms = sorted(list(algorithms))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for alg in algorithms:
        success_rates = []
        for ttl in ttls:
            if alg in ttl_results[ttl]:
                success_rates.append(1 if ttl_results[ttl][alg]["found"] else 0)
            else:
                success_rates.append(0)
        
        ax.plot(ttls, success_rates, marker='o', label=alg, linewidth=2, markersize=8)
    
    ax.set_xlabel('TTL', fontsize=12)
    ax.set_ylabel('Taxa de Sucesso (1=Encontrado, 0=Não Encontrado)', fontsize=12)
    ax.set_title('Taxa de Sucesso vs TTL', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Gráfico TTL salvo em: {output_file}")


def print_results_table(results: Dict[str, Dict]):
    """
    Imprime tabela formatada com os resultados.
    
    Args:
        results: Dicionário {algorithm_name: {messages, nodes_visited, found, path}}
    """
    print("\n" + "="*80)
    print("RESULTADOS DA BUSCA")
    print("="*80)
    print(f"{'Algoritmo':<25} {'Encontrado':<12} {'Mensagens':<12} {'Nós Visitados':<15} {'Tamanho Caminho':<15}")
    print("-"*80)
    
    for alg_name, result in results.items():
        found = "Sim" if result["found"] else "Não"
        messages = result["messages"]
        nodes_visited = result["nodes_visited"]
        path_len = len(result.get("path", []))
        
        print(f"{alg_name:<25} {found:<12} {messages:<12} {nodes_visited:<15} {path_len:<15}")
    
    print("="*80)
    print()
    
    # Mostrar detalhes adicionais
    print("DETALHES DOS CAMINHOS:")
    print("="*80)
    for alg_name, result in results.items():
        print(f"\n{alg_name.upper()}:")
        print(f"  Caminho até encontrar recurso: {' -> '.join(result.get('path', []))}")
        if 'all_visited' in result and result['all_visited']:
            all_visited = result['all_visited']
            if set(all_visited) != set(result.get('path', [])):
                print(f"  Todos os nós visitados: {', '.join(sorted(all_visited))}")
        print()
    print("="*80)

