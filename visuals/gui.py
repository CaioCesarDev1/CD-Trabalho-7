"""
Interface gráfica (GUI) usando Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')  # Backend interativo para GUI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from typing import Optional, Dict
from network import Network


class P2PSimulatorGUI:
    """Interface gráfica para o simulador P2P."""
    
    def __init__(self, root, network: Network):
        """
        Inicializa a GUI.
        
        Args:
            root: Janela principal do Tkinter
            network: Rede P2P
        """
        self.root = root
        self.network = network
        self.root.title("Simulador de Rede P2P")
        self.root.geometry("1400x900")
        
        # Variáveis
        self.algorithm_var = tk.StringVar(value="flooding")
        self.start_node_var = tk.StringVar()
        self.resource_var = tk.StringVar()
        self.ttl_var = tk.IntVar(value=10)
        self.results = {}
        
        self.setup_ui()
        self.draw_initial_network()
    
    def setup_ui(self):
        """Configura a interface."""
        # Frame esquerdo - Controles
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Título
        title_label = ttk.Label(left_frame, text="Simulador P2P", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Algoritmo
        ttk.Label(left_frame, text="Algoritmo:").pack(anchor=tk.W, pady=5)
        algo_combo = ttk.Combobox(left_frame, textvariable=self.algorithm_var,
                                 values=["flooding", "informed_flooding", 
                                        "random_walk", "informed_random_walk"],
                                 state="readonly", width=20)
        algo_combo.pack(pady=5)
        
        # Nó inicial
        ttk.Label(left_frame, text="Nó Inicial:").pack(anchor=tk.W, pady=5)
        nodes = sorted(list(self.network.get_all_nodes()))
        start_combo = ttk.Combobox(left_frame, textvariable=self.start_node_var,
                                  values=nodes, width=20)
        start_combo.pack(pady=5)
        if nodes:
            start_combo.set(nodes[0])
        
        # Recurso
        ttk.Label(left_frame, text="Recurso:").pack(anchor=tk.W, pady=5)
        all_resources = set()
        for resources in self.network.resources.values():
            all_resources.update(resources)
        resource_combo = ttk.Combobox(left_frame, textvariable=self.resource_var,
                                     values=sorted(list(all_resources)), width=20)
        resource_combo.pack(pady=5)
        if all_resources:
            resource_combo.set(sorted(list(all_resources))[0])
        
        # TTL
        ttk.Label(left_frame, text="TTL:").pack(anchor=tk.W, pady=5)
        ttl_spin = ttk.Spinbox(left_frame, from_=1, to=50, 
                              textvariable=self.ttl_var, width=20)
        ttl_spin.pack(pady=5)
        
        # Botão executar
        execute_btn = ttk.Button(left_frame, text="Executar Busca", 
                                command=self.execute_search)
        execute_btn.pack(pady=20)
        
        # Botão executar todos
        execute_all_btn = ttk.Button(left_frame, text="Executar Todos os Algoritmos", 
                                    command=self.execute_all_algorithms)
        execute_all_btn.pack(pady=10)
        
        # Área de resultados
        ttk.Label(left_frame, text="Resultados:", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.results_text = scrolledtext.ScrolledText(left_frame, width=35, height=15)
        self.results_text.pack(pady=5)
        
        # Frame direito - Visualização
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas para o grafo
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def draw_initial_network(self):
        """Desenha a rede inicial."""
        self.draw_network()
    
    def draw_network(self, highlight_node: Optional[str] = None,
                    highlight_path: Optional[list] = None):
        """Desenha a rede no canvas."""
        self.ax.clear()
        
        G = nx.Graph()
        for node in self.network.get_all_nodes():
            G.add_node(node)
        for edge in self.network.edges:
            G.add_edge(edge[0], edge[1])
        
        pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
        
        # Arestas
        nx.draw_networkx_edges(G, pos, ax=self.ax, alpha=0.3, 
                              edge_color='gray', width=1.5)
        
        # Arestas do caminho
        if highlight_path and len(highlight_path) > 1:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                         for i in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, ax=self.ax,
                                  edge_color='red', width=3, alpha=0.7, style='dashed')
        
        # Nós
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            if node == highlight_node:
                node_colors.append('red')
                node_sizes.append(800)
            elif highlight_path and node in highlight_path:
                node_colors.append('orange')
                node_sizes.append(600)
            else:
                node_colors.append('lightblue')
                node_sizes.append(400)
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, ax=self.ax, alpha=0.8)
        
        # Labels
        labels = {}
        for node in G.nodes():
            resources = self.network.resources.get(node, [])
            if resources:
                labels[node] = f"{node}\n{', '.join(resources)}"
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(G, pos, labels, ax=self.ax, 
                               font_size=8, font_weight='bold')
        
        self.ax.set_title("Rede P2P", fontsize=14, fontweight='bold')
        self.ax.axis('off')
        self.canvas.draw()
    
    def execute_search(self):
        """Executa a busca selecionada."""
        algorithm = self.algorithm_var.get()
        start_node = self.start_node_var.get()
        resource = self.resource_var.get()
        ttl = self.ttl_var.get()
        
        if not start_node or not resource:
            messagebox.showerror("Erro", "Preencha nó inicial e recurso!")
            return
        
        # Importar algoritmo
        if algorithm == "flooding":
            from algorithms.flooding import flooding
            result = flooding(self.network, start_node, resource, ttl)
        elif algorithm == "informed_flooding":
            from algorithms.informed_flooding import informed_flooding
            from utils.cache import Cache
            cache = Cache()
            cache.update_from_network(self.network)
            result = informed_flooding(self.network, start_node, resource, ttl, cache)
        elif algorithm == "random_walk":
            from algorithms.random_walk import random_walk
            result = random_walk(self.network, start_node, resource, ttl)
        elif algorithm == "informed_random_walk":
            from algorithms.informed_random_walk import informed_random_walk
            from utils.cache import Cache
            cache = Cache()
            cache.update_from_network(self.network)
            result = informed_random_walk(self.network, start_node, resource, ttl, cache)
        else:
            messagebox.showerror("Erro", "Algoritmo inválido!")
            return
        
        self.results = {algorithm: result}
        
        # Atualizar resultados
        self.update_results_text()
        
        # Atualizar visualização
        highlight_node = None
        if result["found"] and result["path"]:
            highlight_node = result["path"][-1]
        
        self.draw_network(highlight_node=highlight_node, 
                         highlight_path=result.get("path", []))
    
    def execute_all_algorithms(self):
        """Executa todos os algoritmos e compara."""
        start_node = self.start_node_var.get()
        resource = self.resource_var.get()
        ttl = self.ttl_var.get()
        
        if not start_node or not resource:
            messagebox.showerror("Erro", "Preencha nó inicial e recurso!")
            return
        
        from algorithms.flooding import flooding
        from algorithms.informed_flooding import informed_flooding
        from algorithms.random_walk import random_walk
        from algorithms.informed_random_walk import informed_random_walk
        from utils.cache import Cache
        
        results = {}
        
        # Flooding
        results["flooding"] = flooding(self.network, start_node, resource, ttl)
        
        # Informed Flooding
        cache1 = Cache()
        cache1.update_from_network(self.network)
        results["informed_flooding"] = informed_flooding(self.network, start_node, resource, ttl, cache1)
        
        # Random Walk
        results["random_walk"] = random_walk(self.network, start_node, resource, ttl)
        
        # Informed Random Walk
        cache2 = Cache()
        cache2.update_from_network(self.network)
        results["informed_random_walk"] = informed_random_walk(self.network, start_node, resource, ttl, cache2)
        
        self.results = results
        self.update_results_text()
        
        # Mostrar melhor resultado
        best_result = max(results.items(), key=lambda x: (x[1]["found"], -x[1]["messages"]))
        highlight_node = None
        if best_result[1]["found"] and best_result[1]["path"]:
            highlight_node = best_result[1]["path"][-1]
        
        self.draw_network(highlight_node=highlight_node, 
                         highlight_path=best_result[1].get("path", []))
    
    def update_results_text(self):
        """Atualiza a área de resultados."""
        self.results_text.delete(1.0, tk.END)
        
        if not self.results:
            return
        
        text = "="*50 + "\n"
        text += "RESULTADOS\n"
        text += "="*50 + "\n\n"
        
        for alg, result in self.results.items():
            text += f"Algoritmo: {alg.upper()}\n"
            text += f"  Encontrado: {'Sim' if result['found'] else 'Não'}\n"
            text += f"  Mensagens: {result['messages']}\n"
            text += f"  Nós Visitados: {result['nodes_visited']}\n"
            text += f"  Caminho: {' -> '.join(result.get('path', []))}\n"
            text += "\n"
        
        self.results_text.insert(1.0, text)

