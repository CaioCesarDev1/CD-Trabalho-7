"""
Simulador de Rede P2P Não Estruturada
Main entry point do programa.
"""

import json
import sys
import argparse
import time
from typing import Dict, Optional

from network import Network
from utils.validators import validate_network, ValidationError
from algorithms.flooding import flooding
from algorithms.informed_flooding import informed_flooding
from algorithms.random_walk import random_walk
from algorithms.informed_random_walk import informed_random_walk
from utils.cache import Cache
from utils.metrics import create_performance_chart, print_results_table
from visuals.graph_viewer import draw_network


def load_config(config_file: str) -> Dict:
    """Carrega configuração do arquivo JSON."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo {config_file} não encontrado!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erro ao ler JSON: {e}")
        sys.exit(1)


def create_network(config: Dict) -> Network:
    """Cria a rede a partir da configuração."""
    return Network(
        num_nodes=config['num_nodes'],
        resources=config['resources'],
        edges=config['edges']
    )


def run_search(network: Network, algorithm: str, start_node: str, 
               resource: str, ttl: int = 10) -> Dict:
    """
    Executa uma busca usando o algoritmo especificado.
    
    Args:
        network: Rede P2P
        algorithm: Nome do algoritmo ('flooding', 'informed_flooding', etc.)
        start_node: Nó inicial
        resource: Recurso a buscar
        ttl: Time to live
        
    Returns:
        Resultado da busca
    """
    if algorithm == "flooding":
        return flooding(network, start_node, resource, ttl)
    elif algorithm == "informed_flooding":
        cache = Cache()
        cache.update_from_network(network)
        return informed_flooding(network, start_node, resource, ttl, cache)
    elif algorithm == "random_walk":
        return random_walk(network, start_node, resource, ttl)
    elif algorithm == "informed_random_walk":
        cache = Cache()
        cache.update_from_network(network)
        return informed_random_walk(network, start_node, resource, ttl, cache)
    else:
        raise ValueError(f"Algoritmo desconhecido: {algorithm}")


def interactive_mode(network: Network):
    """Modo interativo via CLI."""
    print("\n" + "="*80)
    print("SIMULADOR DE REDE P2P - MODO INTERATIVO")
    print("="*80)
    
    nodes = sorted(list(network.get_all_nodes()))
    all_resources = set()
    for resources in network.resources.values():
        all_resources.update(resources)
    
    print(f"\nNós disponíveis: {', '.join(nodes)}")
    print(f"Recursos disponíveis: {', '.join(sorted(all_resources))}")
    
    while True:
        print("\n" + "-"*80)
        print("Opções:")
        print("1. Executar busca")
        print("2. Executar todos os algoritmos")
        print("3. Visualizar rede")
        print("4. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "1":
            print("\nAlgoritmos disponíveis:")
            print("  - flooding")
            print("  - informed_flooding")
            print("  - random_walk")
            print("  - informed_random_walk")
            
            algorithm = input("Algoritmo: ").strip()
            start_node = input("Nó inicial: ").strip()
            resource = input("Recurso: ").strip()
            
            try:
                ttl = int(input("TTL (padrão 10): ").strip() or "10")
            except ValueError:
                ttl = 10
            
            if algorithm not in ["flooding", "informed_flooding", "random_walk", "informed_random_walk"]:
                print("Algoritmo inválido!")
                continue
            
            if start_node not in nodes:
                print("Nó inicial inválido!")
                continue
            
            start_time = time.time()
            result = run_search(network, algorithm, start_node, resource, ttl)
            elapsed_time = time.time() - start_time
            
            print("\n" + "="*80)
            print("RESULTADO DA BUSCA")
            print("="*80)
            print(f"Algoritmo: {algorithm}")
            print(f"Encontrado: {'Sim' if result['found'] else 'Não'}")
            print(f"Mensagens: {result['messages']}")
            print(f"Nós Visitados: {result['nodes_visited']}")
            print(f"Caminho: {' -> '.join(result.get('path', []))}")
            print(f"Tempo: {elapsed_time:.4f}s")
            print("="*80)
            
            # Visualização
            viz = input("\nVisualizar rede? (s/n): ").strip().lower()
            if viz == 's':
                highlight_node = None
                if result['found'] and result['path']:
                    highlight_node = result['path'][-1]
                draw_network(network, highlight_node=highlight_node, 
                           highlight_path=result.get('path', []))
        
        elif choice == "2":
            start_node = input("Nó inicial: ").strip()
            resource = input("Recurso: ").strip()
            
            try:
                ttl = int(input("TTL (padrão 10): ").strip() or "10")
            except ValueError:
                ttl = 10
            
            if start_node not in nodes:
                print("Nó inicial inválido!")
                continue
            
            algorithms = ["flooding", "informed_flooding", "random_walk", "informed_random_walk"]
            results = {}
            
            print("\nExecutando todos os algoritmos...")
            start_time = time.time()
            
            for alg in algorithms:
                results[alg] = run_search(network, alg, start_node, resource, ttl)
            
            elapsed_time = time.time() - start_time
            
            print_results_table(results)
            print(f"Tempo total: {elapsed_time:.4f}s")
            
            # Gráfico de desempenho
            create_performance_chart(results, "performance.png")
            
            # Visualização
            viz = input("\nVisualizar rede? (s/n): ").strip().lower()
            if viz == 's':
                # Mostrar melhor resultado
                best_result = max(results.items(), key=lambda x: (x[1]["found"], -x[1]["messages"]))
                highlight_node = None
                if best_result[1]['found'] and best_result[1]['path']:
                    highlight_node = best_result[1]['path'][-1]
                draw_network(network, highlight_node=highlight_node, 
                           highlight_path=best_result[1].get('path', []))
        
        elif choice == "3":
            draw_network(network, title="Rede P2P - Visualização Completa")
        
        elif choice == "4":
            print("Saindo...")
            break
        
        else:
            print("Opção inválida!")


def gui_mode(network: Network):
    """Modo GUI."""
    try:
        import tkinter as tk
        from visuals.gui import P2PSimulatorGUI
        
        root = tk.Tk()
        app = P2PSimulatorGUI(root, network)
        root.mainloop()
    except ImportError:
        print("Tkinter não está disponível. Use o modo interativo ou CLI.")
        interactive_mode(network)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Simulador de Rede P2P Não Estruturada')
    parser.add_argument('config_file', help='Arquivo JSON de configuração')
    parser.add_argument('--gui', action='store_true', help='Abrir interface gráfica')
    parser.add_argument('--algorithm', help='Algoritmo a executar (flooding, informed_flooding, random_walk, informed_random_walk)')
    parser.add_argument('--start-node', help='Nó inicial')
    parser.add_argument('--resource', help='Recurso a buscar')
    parser.add_argument('--ttl', type=int, default=10, help='Time to live (padrão: 10)')
    parser.add_argument('--all', action='store_true', help='Executar todos os algoritmos')
    
    args = parser.parse_args()
    
    # Carregar configuração
    print("Carregando configuração...")
    config = load_config(args.config_file)
    
    # Validar
    print("Validando topologia...")
    is_valid, errors = validate_network(config)
    
    if not is_valid:
        print("\nERROS DE VALIDAÇÃO:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    print("✓ Topologia válida!")
    
    # Criar rede
    network = create_network(config)
    print(f"✓ Rede criada com {network.num_nodes} nós")
    
    # Modo GUI
    if args.gui:
        gui_mode(network)
        return
    
    # Modo CLI com parâmetros
    if args.algorithm and args.start_node and args.resource:
        if args.all:
            # Executar todos
            algorithms = ["flooding", "informed_flooding", "random_walk", "informed_random_walk"]
            results = {}
            
            for alg in algorithms:
                results[alg] = run_search(network, alg, args.start_node, args.resource, args.ttl)
            
            print_results_table(results)
            create_performance_chart(results, "performance.png")
            
            # Visualização
            best_result = max(results.items(), key=lambda x: (x[1]["found"], -x[1]["messages"]))
            highlight_node = None
            if best_result[1]['found'] and best_result[1]['path']:
                highlight_node = best_result[1]['path'][-1]
            draw_network(network, highlight_node=highlight_node, 
                       highlight_path=best_result[1].get('path', []),
                       output_file=f"network_all_{args.start_node}_{args.resource}.png")
        else:
            # Executar um algoritmo
            result = run_search(network, args.algorithm, args.start_node, args.resource, args.ttl)
            
            print("\n" + "="*80)
            print("RESULTADO DA BUSCA")
            print("="*80)
            print(f"Algoritmo: {args.algorithm}")
            print(f"Encontrado: {'Sim' if result['found'] else 'Não'}")
            print(f"Mensagens: {result['messages']}")
            print(f"Nós Visitados: {result['nodes_visited']}")
            print(f"Caminho: {' -> '.join(result.get('path', []))}")
            print("="*80)
            
            # Visualização
            highlight_node = None
            if result['found'] and result['path']:
                highlight_node = result['path'][-1]
            draw_network(network, highlight_node=highlight_node, 
                       highlight_path=result.get('path', []),
                       output_file=f"network_{args.algorithm}_{args.start_node}_{args.resource}.png")
    else:
        # Modo interativo
        interactive_mode(network)


if __name__ == "__main__":
    main()

