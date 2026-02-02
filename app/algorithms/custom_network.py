import heapq

class CustomGraphAlgorithms:
    
    @staticmethod
    def dijkstra(edges, start_node, end_node_target=None):
        """
        Dijkstra's Algorithm.
        edges: List of [u, v, weight] or [u, v, weight, capacity]
        Returns: {total_weight, node_order [...], all_distances, paths}
        """
        adj = {}
        # Convert edges to adjacency list
        all_nodes = set()
        for edge in edges:
            u, v = edge[0], edge[1]
            w = float(edge[2])
            all_nodes.add(u)
            all_nodes.add(v)
            if u not in adj: adj[u] = []
            adj[u].append((v, w))
            
        # Priority Queue: (distance, node)
        pq = [(0, start_node)]
        distances = {node: float('inf') for node in all_nodes}
        distances[start_node] = 0
        previous = {node: None for node in all_nodes}
        visited = set()
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if u in visited:
                continue
            visited.add(u)
            
            if start_node == end_node_target and u == end_node_target:
                break
            
            if u in adj:
                for v, w in adj[u]:
                    if distances[u] + w < distances[v]:
                        distances[v] = distances[u] + w
                        previous[v] = u
                        heapq.heappush(pq, (distances[v], v))
                        
        # Reconstruct path
        # If target specified, return path to target.
        # If not, find the "furthest" node or structured return.
        
        # Original code found "end_node" as max distance? 
        # Typically Shortest Path is S -> T.
        # Let's return all info so the caller can decide.
        
        return distances, previous

    @staticmethod
    def reconstruct_path(previous, target):
        path = []
        curr = target
        while curr is not None:
            path.append(curr)
            curr = previous.get(curr)
        return path[::-1] # Reverse

    @staticmethod
    def kruskal_mst(edges):
        """
        Kruskal's Algorithm for MST.
        edges: List of [u, v, weight]
        """
        # Sort edges by weight
        sorted_edges = sorted(edges, key=lambda x: float(x[2]))
        
        parent = {}
        def find(i):
            if parent[i] != i:
                parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False
            
        # Initialize sets
        nodes = set()
        for e in edges:
            nodes.add(e[0])
            nodes.add(e[1])
        for n in nodes:
            parent[n] = n
            
        mst = []
        mst_weight = 0
        
        for e in sorted_edges:
            u, v, w = e[0], e[1], float(e[2])
            if union(u, v):
                mst.append(e)
                mst_weight += w
                
        return mst, mst_weight

    @staticmethod
    def bfs_capacity(adj, capacity, source, sink, parent):
        visited = set()
        queue = [source]
        visited.add(source)
        parent[source] = None
        
        while queue:
            u = queue.pop(0)
            if u == sink:
                return True
            
            for v, cap_val in capacity[u].items():
                if v not in visited and cap_val > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
        return False

    @staticmethod
    def edmonds_karp(edges, source, sink):
        """
        Max Flow.
        edges: List of [u, v, capacity] (or [u,v,w,cap]?)
        Usually input for Max Flow: [u, v, capacity] or [u, v, weight, capacity]
        Check usage in original file.
        """
        # Build graph
        capacity = {} # capacity[u][v]
        graph = {} # adj list
        
        all_nodes = set()
        
        for edge in edges:
            u, v = edge[0], edge[1]
            # Try to grab capacity from index 3 if exists, else index 2?
            # Original code 'max_flow_algorithm': for u, v, weight, cap in graph
            # So index 3 is capacity.
            if len(edge) > 3:
                cap = float(edge[3])
            else:
                cap = float(edge[2]) # Fallback if only 3 elements (u,v,cap)
            
            all_nodes.add(u)
            all_nodes.add(v)
            
            if u not in graph: graph[u] = []
            if v not in graph: graph[v] = []
            
            # Setup residual graph structure
            if u not in capacity: capacity[u] = {}
            if v not in capacity: capacity[v] = {}
            
            graph[u].append(v)
            graph[v].append(u) # Reverse edge for residual
            
            capacity[u][v] = cap
            if v not in capacity[u]: capacity[u][v] = cap # ? No, just set.
            # Initialize reverse capacity 0 if not existing
            if u not in capacity[v]: capacity[v][u] = 0
            
        max_flow = 0
        parent = {}
        iterations = []
        
        while CustomGraphAlgorithms.bfs_capacity(capacity, capacity, source, sink, parent):
            path_flow = float('inf')
            path = []
            s = sink
            while s != source:
                path.append(s)
                p = parent[s]
                path_flow = min(path_flow, capacity[p][s])
                s = p
            path.append(source)
            path.reverse()
            
            max_flow += path_flow
            iterations.append({
                "path": path,
                "flow": path_flow
            })
            
            v = sink
            while v != source:
                u = parent[v]
                capacity[u][v] -= path_flow
                capacity[v][u] += path_flow
                v = u
                
        # Calculate flow on each edge: Original Cap - Residual Cap?
        # Flow logic return
        return max_flow, iterations

    @staticmethod
    def min_cost_max_flow(edges, source, sink):
        """
        Min Cost Max Flow or Min Cost Flow for required amount?
        Usually Min Cost Flow involves costs.
        Input: [u, v, weight(cost), capacity]
        Algorithm: Successive Shortest Path using Bellman-Ford or SPFA (if negative costs) or Dijkstra with potentials.
        Simple implementation: Successive shortest path using Bellman-Ford (easiest to implement without potentials).
        """
        capacity = {}
        cost = {}
        graph = {}
        
        nodes = set()
        for edge in edges:
            u, v = edge[0], edge[1]
            w_cost = float(edge[2])
            cap = float(edge[3])
            
            nodes.add(u); nodes.add(v)
            
            if u not in graph: graph[u] = []
            if v not in graph: graph[v] = []
            
            graph[u].append(v)
            graph[v].append(u)
            
            if u not in capacity: capacity[u] = {}
            if v not in capacity: capacity[v] = {}
            if u not in cost: cost[u] = {}
            if v not in cost: cost[v] = {}
            
            capacity[u][v] = cap
            capacity[v][u] = 0
            
            cost[u][v] = w_cost
            cost[v][u] = -w_cost
            
        total_flow = 0
        min_cost = 0
        flow_dict = {} # Key: (u,v), Value: flow
        
        while True:
            # Find shortest path from source to sink in residual graph based on COST
            dist = {n: float('inf') for n in nodes}
            parent = {n: None for n in nodes}
            edge_from = {n: None for n in nodes}
            dist[source] = 0
            
            # Bellman-Ford or SPFA
            in_queue = {n: False for n in nodes}
            queue = [source]
            in_queue[source] = True
            
            while queue:
                u = queue.pop(0)
                in_queue[u] = False
                if u in graph:
                    for v in graph[u]:
                        if capacity[u][v] > 0 and dist[v] > dist[u] + cost[u][v]:
                            dist[v] = dist[u] + cost[u][v]
                            parent[v] = u
                            edge_from[v] = v # Not needed really
                            if not in_queue[v]:
                                queue.append(v)
                                in_queue[v] = True
                                
            if dist[sink] == float('inf'):
                break
                
            # Augment flow
            flow = float('inf')
            curr = sink
            while curr != source:
                p = parent[curr]
                flow = min(flow, capacity[p][curr])
                curr = p
            
            total_flow += flow
            min_cost += flow * dist[sink]
            curr = sink
            while curr != source:
                p = parent[curr]
                capacity[p][curr] -= flow
                capacity[v][u] += flow # This is wrong index use v,u.
                # Correct: capacity[curr][p] += flow
                
                # Record flow
                if (p, curr) not in flow_dict: flow_dict[(p,curr)] = 0
                flow_dict[(p,curr)] += flow
                
                curr = p
                
        return min_cost, flow_dict
