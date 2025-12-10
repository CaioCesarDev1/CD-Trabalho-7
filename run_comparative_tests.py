"""
Script para executar testes comparativos dos algoritmos de busca
em diferentes topologias de rede P2P.
"""

import json
import os
import time
from typing import Dict, List
import matplotlib.pyplot as plt
import pandas as pd
from network import Network
from utils.validators import validate_network
from algorithms.flooding import flooding
from algorithms.informed_flooding import informed_flooding
from algorithms.random_walk import random_walk
from algorithms.informed_random_walk import informed_random_walk
from utils.cache import Cache

# Configurações de teste
ALGORITHMS = ["flooding", "informed_flooding", "random_walk", "informed_random_walk"]
TTL_VALUES = [5, 10, 15, 20]
NUM_RUNS_RANDOM = 5  # Número de execuções para algoritmos aleatórios (média)

def load_and_validate_config(config_file: str):
    """Carrega e valida configuração."""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    is_valid, errors = validate_network(config)
    if not is_valid:
        print(f"ERRO: {config_file} é inválido:")
        for error in errors:
            print(f"  - {error}")
        return None
    
    return config

def run_algorithm(network: Network, algorithm: str, start_node: str, 
                 resource: str, ttl: int) -> Dict:
    """Executa um algoritmo de busca."""
    if algorithm == "flooding":
        return flooding(network, start_node, resource, ttl)
    elif algorithm == "informed_flooding":
        cache = Cache()
        cache.update_from_network(network)
        return informed_flooding(network, start_node, resource, ttl, cache)
    elif algorithm == "random_walk":
        # Para random walk, executar múltiplas vezes e fazer média
        results = []
        for _ in range(NUM_RUNS_RANDOM):
            results.append(random_walk(network, start_node, resource, ttl))
        # Calcular média
        avg_messages = sum(r['messages'] for r in results) / len(results)
        avg_nodes = sum(r['nodes_visited'] for r in results) / len(results)
        found_any = any(r['found'] for r in results)
        return {
            'found': found_any,
            'messages': int(avg_messages),
            'nodes_visited': int(avg_nodes),
            'path': results[0]['path'] if results else []
        }
    elif algorithm == "informed_random_walk":
        # Para informed random walk, executar múltiplas vezes e fazer média
        results = []
        for _ in range(NUM_RUNS_RANDOM):
            cache = Cache()
            cache.update_from_network(network)
            results.append(informed_random_walk(network, start_node, resource, ttl, cache))
        # Calcular média
        avg_messages = sum(r['messages'] for r in results) / len(results)
        avg_nodes = sum(r['nodes_visited'] for r in results) / len(results)
        found_any = any(r['found'] for r in results)
        return {
            'found': found_any,
            'messages': int(avg_messages),
            'nodes_visited': int(avg_nodes),
            'path': results[0]['path'] if results else []
        }
    else:
        raise ValueError(f"Algoritmo desconhecido: {algorithm}")

def test_topology(config_file: str, topology_name: str):
    """Testa uma topologia específica."""
    print(f"\n{'='*80}")
    print(f"Testando topologia: {topology_name}")
    print(f"Arquivo: {config_file}")
    print('='*80)
    
    config = load_and_validate_config(config_file)
    if not config:
        return None
    
    network = Network(config['num_nodes'], config['resources'], config['edges'])
    
    # Escolher nó inicial e recurso alvo (buscando recurso do último nó)
    nodes = sorted(list(network.get_all_nodes()))
    start_node = nodes[0]
    target_node = nodes[-1]
    target_resource = config['resources'][target_node][0]
    
    print(f"Nó inicial: {start_node}")
    print(f"Recurso buscado: {target_resource} (em {target_node})")
    print()
    
    results = {}
    
    for ttl in TTL_VALUES:
        results[ttl] = {}
        print(f"  TTL = {ttl}:")
        
        for algorithm in ALGORITHMS:
            result = run_algorithm(network, algorithm, start_node, target_resource, ttl)
            results[ttl][algorithm] = result
            
            status = "✓" if result['found'] else "✗"
            print(f"    {status} {algorithm:20s} - Mensagens: {result['messages']:4d}, "
                  f"Nós: {result['nodes_visited']:3d}, Encontrado: {result['found']}")
    
    return {
        'topology': topology_name,
        'num_nodes': config['num_nodes'],
        'start_node': start_node,
        'target_resource': target_resource,
        'results': results
    }

def generate_comparative_charts(all_results: List[Dict]):
    """Gera gráficos comparativos."""
    print("\n" + "="*80)
    print("GERANDO GRÁFICOS COMPARATIVOS")
    print("="*80)
    
    # Preparar dados
    data = []
    for test_result in all_results:
        topology = test_result['topology']
        num_nodes = test_result['num_nodes']
        
        for ttl, algo_results in test_result['results'].items():
            for algo, result in algo_results.items():
                data.append({
                    'Topologia': topology,
                    'Nós': num_nodes,
                    'TTL': ttl,
                    'Algoritmo': algo,
                    'Mensagens': result['messages'],
                    'Nós Visitados': result['nodes_visited'],
                    'Encontrado': 1 if result['found'] else 0
                })
    
    df = pd.DataFrame(data)
    
    # Gráfico 1: Mensagens por algoritmo (média entre topologias)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Mensagens médias por algoritmo
    ax1 = axes[0, 0]
    msg_by_algo = df.groupby('Algoritmo')['Mensagens'].mean().sort_values()
    msg_by_algo.plot(kind='bar', ax=ax1, color='skyblue', edgecolor='navy', alpha=0.7)
    ax1.set_title('Mensagens Médias por Algoritmo', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Algoritmo', fontsize=12)
    ax1.set_ylabel('Mensagens', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    for i, v in enumerate(msg_by_algo):
        ax1.text(i, v + max(msg_by_algo) * 0.01, f'{int(v)}', ha='center', va='bottom')
    
    # 2. Nós visitados médios por algoritmo
    ax2 = axes[0, 1]
    nodes_by_algo = df.groupby('Algoritmo')['Nós Visitados'].mean().sort_values()
    nodes_by_algo.plot(kind='bar', ax=ax2, color='lightcoral', edgecolor='darkred', alpha=0.7)
    ax2.set_title('Nós Visitados Médios por Algoritmo', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Algoritmo', fontsize=12)
    ax2.set_ylabel('Nós Visitados', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    for i, v in enumerate(nodes_by_algo):
        ax2.text(i, v + max(nodes_by_algo) * 0.01, f'{int(v)}', ha='center', va='bottom')
    
    # 3. Mensagens vs TTL por algoritmo
    ax3 = axes[1, 0]
    for algo in ALGORITHMS:
        algo_data = df[df['Algoritmo'] == algo].groupby('TTL')['Mensagens'].mean()
        ax3.plot(algo_data.index, algo_data.values, marker='o', label=algo, linewidth=2, markersize=8)
    ax3.set_title('Mensagens vs TTL por Algoritmo', fontsize=14, fontweight='bold')
    ax3.set_xlabel('TTL', fontsize=12)
    ax3.set_ylabel('Mensagens Médias', fontsize=12)
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # 4. Taxa de sucesso por algoritmo
    ax4 = axes[1, 1]
    success_by_algo = df.groupby('Algoritmo')['Encontrado'].mean() * 100
    success_by_algo.plot(kind='bar', ax=ax4, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
    ax4.set_title('Taxa de Sucesso por Algoritmo (%)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Algoritmo', fontsize=12)
    ax4.set_ylabel('Taxa de Sucesso (%)', fontsize=12)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', alpha=0.3)
    for i, v in enumerate(success_by_algo):
        ax4.text(i, v + max(success_by_algo) * 0.01, f'{v:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('comparative_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico salvo em: comparative_analysis.png")
    
    # Gráfico 2: Comparação por topologia
    fig2, axes2 = plt.subplots(2, 1, figsize=(14, 10))
    
    # Mensagens por topologia
    ax5 = axes2[0]
    topology_msg = df.groupby(['Topologia', 'Algoritmo'])['Mensagens'].mean().unstack()
    topology_msg.plot(kind='bar', ax=ax5, width=0.8)
    ax5.set_title('Mensagens Médias por Topologia e Algoritmo', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Topologia', fontsize=12)
    ax5.set_ylabel('Mensagens', fontsize=12)
    ax5.legend(title='Algoritmo', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(axis='y', alpha=0.3)
    
    # Nós visitados por topologia
    ax6 = axes2[1]
    topology_nodes = df.groupby(['Topologia', 'Algoritmo'])['Nós Visitados'].mean().unstack()
    topology_nodes.plot(kind='bar', ax=ax6, width=0.8)
    ax6.set_title('Nós Visitados Médios por Topologia e Algoritmo', fontsize=14, fontweight='bold')
    ax6.set_xlabel('Topologia', fontsize=12)
    ax6.set_ylabel('Nós Visitados', fontsize=12)
    ax6.legend(title='Algoritmo', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('topology_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico salvo em: topology_comparison.png")
    
    # Salvar dados em CSV
    df.to_csv('test_results.csv', index=False)
    print("✓ Dados salvos em: test_results.csv")
    
    # Estatísticas resumidas
    print("\n" + "="*80)
    print("ESTATÍSTICAS RESUMIDAS")
    print("="*80)
    print("\nMensagens médias por algoritmo:")
    print(df.groupby('Algoritmo')['Mensagens'].agg(['mean', 'std', 'min', 'max']).round(2))
    print("\nNós visitados médios por algoritmo:")
    print(df.groupby('Algoritmo')['Nós Visitados'].agg(['mean', 'std', 'min', 'max']).round(2))
    print("\nTaxa de sucesso por algoritmo:")
    print((df.groupby('Algoritmo')['Encontrado'].mean() * 100).round(2))

def main():
    """Função principal."""
    print("="*80)
    print("TESTES COMPARATIVOS DE ALGORITMOS P2P")
    print("="*80)
    
    # Lista de topologias para testar
    topologies = [
        ("tests/sample_config.json", "Original (6 nós)"),
        ("tests/topology_star.json", "Estrela (7 nós)"),
        ("tests/topology_ring.json", "Anel (8 nós)"),
        ("tests/topology_mesh.json", "Malha Completa (5 nós)"),
        ("tests/topology_tree.json", "Árvore (7 nós)"),
        ("tests/topology_large.json", "Grande (12 nós)"),
        ("tests/topology_cluster.json", "Clusters (10 nós)"),
        ("tests/topology_line.json", "Linha (6 nós)")
    ]
    
    all_results = []
    
    for config_file, topology_name in topologies:
        if not os.path.exists(config_file):
            print(f"⚠️  Arquivo não encontrado: {config_file}")
            continue
        
        result = test_topology(config_file, topology_name)
        if result:
            all_results.append(result)
    
    if all_results:
        generate_comparative_charts(all_results)
        print("\n" + "="*80)
        print("TESTES CONCLUÍDOS COM SUCESSO!")
        print("="*80)
    else:
        print("\n❌ Nenhum teste foi executado com sucesso.")

if __name__ == "__main__":
    main()

