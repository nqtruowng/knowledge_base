from graph_builder import GraphBuilder
import copy

class BackwardChainer:
    def __init__(self, rules, gt_str, kl_str, method):
        self.rules = copy.deepcopy(rules)
        self.gt = set(f.strip() for f in gt_str.split(',') if f.strip())
        self.kl_str = kl_str.strip()
        self.method = method
        
        self.summary_log = [] # Log tóm tắt (Bắt đầu, Kết luận, VET)
        self.vet = []
        
        self.graph_builder = None
        if self.method == 'fpg':
            self.graph_builder = GraphBuilder(self.rules)
            
        self.graph_nodes = []
        self.graph_edges = []
        self.node_counter = 0

    def _format_set(self, s):
        return ','.join(sorted(list(s)))

    def _format_list(self, l):
        return ','.join(map(str, l))

    def _find_rules_for_goal(self, goal):
        return [i for i, rule in enumerate(self.rules) if rule['right'] == goal]

    def _select_rules(self, rule_indices):
        if not rule_indices:
            return []
        if self.method == 'min':
            return sorted(rule_indices)
        if self.method == 'max':
            return sorted(rule_indices, reverse=True)
        if self.method == 'fpg':
            # (Logic FPG của bạn giữ nguyên, không thay đổi)
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
        return sorted(rule_indices)

    # 🚩 YÊU CẦU: THAY ĐỔI LỚN
    # Hàm _prove giờ trả về 1 dictionary (log_node) thay vì boolean
    def _prove(self, goal, path, path_node_map, parent_node_id=None):
        """
        Hàm đệ quy chứng minh mục tiêu (goal).
        Trả về một đối tượng node cho cây log.
        """
        
        # 1. Tạo Node Log và Node Đồ Thị
        log_node = {
            'text': f"Cần chứng minh: {goal}",
            'status': 'pending', # (Trạng thái: pending, gt, loop, failed, proven)
            'children': []
        }
        
        current_node_id = self.node_counter
        self.node_counter += 1
        graph_node_data = {'id': current_node_id, 'label': goal}
        
        if parent_node_id is not None:
            self.graph_edges.append({'from': current_node_id, 'to': parent_node_id})

        # 2. Kiểm tra GT (Base case 1)
        if goal in self.gt:
            log_node['status'] = 'gt'
            log_node['text'] = f"{goal} (Có trong GT ✅)"
            graph_node_data['group'] = 'gt'
            self.graph_nodes.append(graph_node_data)
            return log_node
            
        # 3. Kiểm tra vòng lặp (Base case 2)
        if goal in path:
            log_node['status'] = 'loop'
            log_node['text'] = f"{goal} (Phát hiện lặp 🔄)"
            graph_node_data['group'] = 'loop'
            graph_node_data['label'] += ' (Lặp)'
            self.graph_nodes.append(graph_node_data)
            
            original_node_id = path_node_map[goal]
            self.graph_edges.append({
                'from': original_node_id, 
                'to': current_node_id, 
                'label': 'Quay lui', 
                'dashes': True
            })
            return log_node
            
        self.graph_nodes.append(graph_node_data)
        path_node_map[goal] = current_node_id

        # 4. Tìm luật
        applicable_rule_indices = self._find_rules_for_goal(goal)
        if not applicable_rule_indices:
            log_node['status'] = 'failed'
            log_node['text'] = f"{goal} (Không có luật sinh ra ❌)"
            graph_node_data['group'] = 'failed'
            return log_node
            
        # 5. Sắp xếp luật (THOA)
        thoa = self._select_rules(applicable_rule_indices)
        
        # 6. Thử từng luật (Recursive step)
        for r_index in thoa:
            rule = self.rules[r_index]
            
            # Tạo node log cho việc "Thử luật"
            rule_log_node = {
                'text': f"Thử luật r{r_index+1}: {rule['raw_left']} -> {rule['right']}",
                'status': 'pending',
                'children': []
            }
            
            # Tạo node đồ thị cho luật (nút AND)
            rule_node_id = self.node_counter
            self.node_counter += 1
            premise_label = ','.join(sorted(list(rule['left'])))
            rule_graph_node_data = {
                'id': rule_node_id, 
                'label': f'{{{premise_label}}} (r{r_index+1})',
                'shape': 'box'
            }
            self.graph_nodes.append(rule_graph_node_data)
            self.graph_edges.append({'from': rule_node_id, 'to': current_node_id})

            all_premises_proven = True
            premises = sorted(list(rule['left']))
            
            for premise in premises:
                # Đệ quy chứng minh từng tiền đề
                premise_log_node = self._prove(premise, path + [goal], path_node_map.copy(), rule_node_id)
                
                # Thêm kết quả (con) vào node "Thử luật"
                rule_log_node['children'].append(premise_log_node)
                
                if premise_log_node['status'] not in ['proven', 'gt']:
                    all_premises_proven = False
                    rule_graph_node_data['group'] = 'failed'
                    rule_log_node['status'] = 'failed'
                    break # Thất bại 1 tiền đề -> dừng thử luật này
            
            # Thêm node "Thử luật" (dù thất bại hay thành công) vào node "Mục tiêu"
            log_node['children'].append(rule_log_node)

            if all_premises_proven:
                rule_log_node['status'] = 'proven'
                log_node['status'] = 'proven'
                log_node['text'] = f"{goal} (Đã chứng minh ✔️)"
                
                self.vet.append(r_index + 1)
                graph_node_data['group'] = 'proven'
                rule_graph_node_data['group'] = 'proven'
                
                # Trả về ngay khi tìm thấy 1 cách chứng minh
                return log_node 
                
        # 7. Nếu thử hết luật mà không thành công
        log_node['status'] = 'failed'
        log_node['text'] = f"{goal} (Thất bại, hết luật ❌)"
        graph_node_data['group'] = 'failed'
        return log_node

    def run(self):
        """Thực thi thuật toán suy diễn lùi."""
        if not self.kl_str:
            return {'status': 'Lỗi', 'summary_log': ['Vui lòng nhập một mục tiêu (Kết luận)']}
            
        self.graph_nodes = []
        self.graph_edges = []
        self.node_counter = 0
        self.summary_log = [] # Reset log
            
        self.summary_log.append(f"Bắt đầu suy diễn lùi cho mục tiêu: {self.kl_str}")
        self.summary_log.append(f"Giả thiết (GT): {{{self._format_set(self.gt)}}}")
        self.summary_log.append(f"Phương pháp chọn luật: {self.method.upper()}")
        self.summary_log.append("-" * 20)
        
        # Gọi hàm đệ quy mới
        log_tree_root = self._prove(self.kl_str, [], {})
        
        is_proven = log_tree_root['status'] in ['proven', 'gt']
        
        self.summary_log.append("-" * 20)
        if is_proven:
            result = "Thành công"
            self.summary_log.append(f"Kết luận: {result}. Mục tiêu {self.kl_str} đã được chứng minh.")
            self.vet.reverse()
            self.summary_log.append(f"Vết suy diễn (VET): {self._format_list(self.vet)}")
        else:
            result = "Thất bại"
            self.summary_log.append(f"Kết luận: {result}. Không thể chứng minh mục tiêu {self.kl_str}.")
            
        return {
            'status': result, 
            'summary_log': self.summary_log, # Log tóm tắt
            'log_tree': log_tree_root,    # Cây log chi tiết
            'vet': self.vet,
            'graph_data': {'nodes': self.graph_nodes, 'edges': self.graph_edges}
        }