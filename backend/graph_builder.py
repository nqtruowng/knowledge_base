import networkx as nx

class GraphBuilder:
    def __init__(self, rules):
        # rules là list dạng [{'left': {'a', 'b'}, 'right': 'c'}, ...]
        self.rules = rules
        self.facts = set()
        for rule in rules:
            self.facts.update(rule['left'])
            self.facts.add(rule['right'])
        
        self.fpg = None
        self.rpg = None

    def _build_fpg(self):
        """Xây dựng đồ thị FPG (Facts Precedence Graph)."""
        G = nx.DiGraph()
        # Thêm tất cả sự kiện làm node
        G.add_nodes_from(self.facts)
        
        # Thêm các cung
        for i, rule in enumerate(self.rules):
            q = rule['right']
            for f in rule['left']:
                G.add_edge(f, q, label=f'r{i+1}')
        self.fpg = G
        return G

    def _build_rpg(self):
        """Xây dựng đồ thị RPG (Rules Precedence Graph)."""
        G = nx.DiGraph()
        num_rules = len(self.rules)
        rule_nodes = [f'r{i+1}' for i in range(num_rules)]
        G.add_nodes_from(rule_nodes)
        
        for i in range(num_rules):
            ri = self.rules[i]
            f = ri['right'] # Sự kiện mà luật i sinh ra
            
            for j in range(num_rules):
                if i == j:
                    continue
                rj = self.rules[j]
                # Nếu f nằm trong vế trái của rj (ri là liên hệ trước của rj)
                if f in rj['left']:
                    G.add_edge(f'r{i+1}', f'r{j+1}')
        self.rpg = G
        return G

    def _get_nx_graph_data(self, G, gt_nodes=None, kl_nodes=None):
        """Chuyển đổi đồ thị networkx sang định dạng JSON cho vis.js."""
        nodes = []
        for node in G.nodes():
            data = {'id': node, 'label': str(node)}
            if gt_nodes and node in gt_nodes:
                data['group'] = 'gt'
            elif kl_nodes and node in kl_nodes:
                data['group'] = 'kl'
            nodes.append(data)
            
        edges = []
        for u, v, data in G.edges(data=True):
            edge_data = {'from': u, 'to': v}
            if 'label' in data:
                edge_data['label'] = data['label']
            edges.append(edge_data)
            
        return {'nodes': nodes, 'edges': edges}

    def build_fpg_data(self, gt=None, kl=None):
        """Lấy dữ liệu FPG cho frontend."""
        if not self.fpg:
            self._build_fpg()
        return self._get_nx_graph_data(self.fpg, gt, kl)

    def build_rpg_data(self, gt=None, kl=None):
        """Lấy dữ liệu RPG cho frontend."""
        if not self.rpg:
            self._build_rpg()
        
        # Xác định RGT và RKL
        rgt_nodes = set()
        if gt:
            for i, rule in enumerate(self.rules):
                if rule['left'].issubset(gt):
                    rgt_nodes.add(f'r{i+1}')

        rkl_nodes = set()
        if kl:
             for i, rule in enumerate(self.rules):
                if rule['right'] in kl:
                    rkl_nodes.add(f'r{i+1}')
                    
        return self._get_nx_graph_data(self.rpg, rgt_nodes, rkl_nodes)

    def get_fpg_distance(self, start_node, end_nodes):
        """Tính khoảng cách ngắn nhất từ start_node đến bất kỳ node nào trong end_nodes trên FPG."""
        if not self.fpg:
            self._build_fpg()
            
        min_dist = float('inf')
        if start_node not in self.fpg:
            return min_dist # Node không tồn tại trên đồ thị
            
        for end_node in end_nodes:
            if end_node in self.fpg and nx.has_path(self.fpg, start_node, end_node):
                try:
                    dist = nx.shortest_path_length(self.fpg, start_node, end_node)
                    if dist < min_dist:
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue
        return min_dist

    def get_rpg_distance(self, start_rule_index, end_rule_indices):
        """Tính khoảng cách ngắn nhất từ luật bắt đầu đến tập luật kết thúc trên RPG."""
        if not self.rpg:
            self._build_rpg()
            
        start_node = f'r{start_rule_index + 1}'
        end_nodes = [f'r{i + 1}' for i in end_rule_indices]
        
        min_dist = float('inf')
        if start_node not in self.rpg:
            return min_dist
            
        for end_node in end_nodes:
            if end_node in self.rpg and nx.has_path(self.rpg, start_node, end_node):
                try:
                    dist = nx.shortest_path_length(self.rpg, start_node, end_node)
                    if dist < min_dist:
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue
        return min_dist

    def get_fpg_distance_to_gt(self, start_node, gt_nodes):
        """Tính khoảng cách ngắn nhất TỪ GT tới start_node (dùng cho suy diễn lùi)."""
        if not self.fpg:
            self._build_fpg()
        
        min_dist = float('inf')
        if start_node in gt_nodes:
            return 0 # Đã có trong GT
        
        if start_node not in self.fpg:
            return min_dist
            
        for gt_node in gt_nodes:
            if gt_node in self.fpg and nx.has_path(self.fpg, gt_node, start_node):
                try:
                    dist = nx.shortest_path_length(self.fpg, gt_node, start_node)
                    if dist < min_dist:
                        min_dist = dist
                except nx.NetworkXNoPath:
                    continue
        return min_dist