from graph_builder import GraphBuilder
import copy

class BackwardChainer:
    def __init__(self, rules, gt_str, kl_str, method):
        self.rules = copy.deepcopy(rules) # List dạng [{'left': {'a', 'b'}, 'right': 'c'}, ...]
        self.gt = set(f.strip() for f in gt_str.split(',') if f.strip())
        self.kl_str = kl_str.strip() # Giả định suy diễn lùi 1 mục tiêu
        self.method = method # 'min', 'max', 'fpg'
        
        self.log = []
        self.vet = [] # Vết suy diễn (thứ tự ngược)
        
        self.graph_builder = None
        if self.method == 'fpg':
            self.graph_builder = GraphBuilder(self.rules)
            
        # 🚩 THÊM MỚI (YÊU CẦU 2): Dữ liệu cho đồ thị tìm kiếm
        self.graph_nodes = []
        self.graph_edges = []
        self.node_counter = 0

    def _format_set(self, s):
        """Helper: Định dạng set thành chuỗi 'a,b,c'."""
        return ','.join(sorted(list(s)))

    def _format_list(self, l):
        """Helper: Định dạng list thành chuỗi '1,2,3'."""
        return ','.join(map(str, l))

    def _find_rules_for_goal(self, goal):
        """Tìm các luật (theo index) có vế phải là goal."""
        return [i for i, rule in enumerate(self.rules) if rule['right'] == goal]

    def _select_rules(self, rule_indices):
        """Sắp xếp/chọn luật từ THOA(f) theo phương pháp."""
        if not rule_indices:
            return []
            
        if self.method == 'min':
            return sorted(rule_indices)
        if self.method == 'max':
            return sorted(rule_indices, reverse=True)
        
        if self.method == 'fpg':
            rule_heuristics = []
            for r_index in rule_indices:
                rule = self.rules[r_index]
                max_dist = 0
                for f in rule['left']:
                    dist = self.graph_builder.get_fpg_distance_to_gt(f, self.gt)
                    if dist == float('inf'):
                        max_dist = float('inf') 
                        break
                    if dist > max_dist:
                        max_dist = dist
                rule_heuristics.append((r_index, max_dist))
            
            rule_heuristics.sort(key=lambda x: (x[1], x[0]))
            return [r_index for r_index, h_val in rule_heuristics]
            
        return sorted(rule_indices) # Mặc định là min

    # 🚩 SỬA ĐỔI (YÊU CẦU 2): Sửa hàm _prove để xây dựng đồ thị
    def _prove(self, goal, path, path_node_map, parent_node_id=None):
        """
        Hàm đệ quy chứng minh mục tiêu (goal).
        parent_node_id: ID của nút cha (để vẽ cạnh)
        path_node_map: dict theo dõi {goal: node_id} trên đường dẫn để phát hiện lặp
        """
        indent = "  " * len(path)
        self.log.append(f"{indent}Cần chứng minh: {goal}")

        # Tạo nút cho mục tiêu (goal) này
        current_node_id = self.node_counter
        self.node_counter += 1
        node_data = {'id': current_node_id, 'label': goal}
        
        # Thêm cạnh từ cha (nếu có) đến nút này
        if parent_node_id is not None:
            self.graph_edges.append({'from': parent_node_id, 'to': current_node_id})

        # 1. Kiểm tra GT
        if goal in self.gt:
            self.log.append(f"{indent}-> {goal} đã có trong GT. (True)")
            node_data['group'] = 'gt' # Tô màu GT
            self.graph_nodes.append(node_data)
            return True
            
        # 2. Kiểm tra vòng lặp
        if goal in path:
            self.log.append(f"{indent}-> Phát hiện vòng lặp (Quay lui): {goal} đã có trong đường dẫn.")
            node_data['group'] = 'loop'
            node_data['label'] += ' (Lặp)'
            self.graph_nodes.append(node_data)
            
            # Thêm cạnh "quay lui"
            original_node_id = path_node_map[goal]
            self.graph_edges.append({
                'from': current_node_id, 
                'to': original_node_id, 
                'label': 'Quay lui', 
                'dashes': True
            })
            return False
            
        # Thêm nút vào đồ thị (sau khi check GT/Lặp)
        self.graph_nodes.append(node_data)
        path_node_map[goal] = current_node_id # Lưu id của nút này vào đường dẫn

        # 3. Tìm luật
        applicable_rule_indices = self._find_rules_for_goal(goal)
        if not applicable_rule_indices:
            self.log.append(f"{indent}-> Không có luật nào sinh ra {goal}. (False)")
            node_data['group'] = 'failed' # Tô màu thất bại
            return False
            
        # 4. Sắp xếp luật (THOA(f))
        thoa = self._select_rules(applicable_rule_indices)
        self.log.append(f"{indent}Các luật áp dụng (theo thứ tự {self.method}): {[f'r{i+1}' for i in thoa]}")
        
        # 5. Thử từng luật
        for r_index in thoa:
            rule = self.rules[r_index]
            self.log.append(f"{indent}Thử luật r{r_index+1}: {rule['raw_left']} -> {rule['right']}")
            
            # Tạo một "nút luật" (nút AND)
            rule_node_id = self.node_counter
            self.node_counter += 1
            premise_label = ','.join(sorted(list(rule['left'])))
            rule_node_data = {
                'id': rule_node_id, 
                'label': f'{{{premise_label}}} (r{r_index+1})',
                'shape': 'box' # Nút luật là hình hộp
            }
            self.graph_nodes.append(rule_node_data)
            # Nối 'goal' -> 'nút luật'
            self.graph_edges.append({'from': current_node_id, 'to': rule_node_id})

            all_premises_proven = True
            premises = sorted(list(rule['left'])) # Chứng minh theo thứ tự alpha
            
            for premise in premises:
                # Đệ quy chứng minh từng tiền đề
                # Nút cha là 'nút luật' (rule_node_id)
                if not self._prove(premise, path + [goal], path_node_map.copy(), rule_node_id):
                    all_premises_proven = False
                    self.log.append(f"{indent}-> Tiền đề {premise} của r{r_index+1} thất bại. (Quay lui)")
                    rule_node_data['group'] = 'failed' # Tô màu nút luật thất bại
                    break # Thử luật tiếp theo
            
            if all_premises_proven:
                self.log.append(f"{indent}-> Tất cả tiền đề của r{r_index+1} là True.")
                self.log.append(f"{indent}-> {goal} được chứng minh là True.")
                self.vet.append(r_index + 1) # Thêm vào VET
                node_data['group'] = 'proven' # Tô màu nút goal thành công
                rule_node_data['group'] = 'proven' # Tô màu nút luật thành công
                return True
                
        # 6. Nếu thử hết luật mà không thành công
        self.log.append(f"{indent}-> Đã thử hết luật cho {goal} nhưng thất bại. (False)")
        node_data['group'] = 'failed' # Tô màu nút goal thất bại
        return False

    def run(self):
        """Thực thi thuật toán suy diễn lùi."""
        if not self.kl_str:
            return {'status': 'Lỗi', 'log': ['Vui lòng nhập một mục tiêu (Kết luận)']}
            
        # Reset đồ thị
        self.graph_nodes = []
        self.graph_edges = []
        self.node_counter = 0
            
        self.log.append(f"Bắt đầu suy diễn lùi cho mục tiêu: {self.kl_str}")
        self.log.append(f"Giả thiết (GT): {{{self._format_set(self.gt)}}}")
        self.log.append(f"Phương pháp chọn luật: {self.method.upper()}")
        self.log.append("-" * 20)
        
        is_proven = self._prove(self.kl_str, [], {})
        
        self.log.append("-" * 20)
        if is_proven:
            result = "Thành công"
            self.log.append(f"Kết luận: {result}. Mục tiêu {self.kl_str} đã được chứng minh.")
            self.vet.reverse()
            self.log.append(f"Vết suy diễn (VET): {self._format_list(self.vet)}")
        else:
            result = "Thất bại"
            self.log.append(f"Kết luận: {result}. Không thể chứng minh mục tiêu {self.kl_str}.")
            
        return {
            'status': result, 
            'log': self.log, 
            'vet': self.vet,
            'graph_data': {'nodes': self.graph_nodes, 'edges': self.graph_edges}
        }