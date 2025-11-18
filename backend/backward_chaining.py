from graph_builder import GraphBuilder
import copy

class BackwardChainer:
    def __init__(self, rules, gt_str, kl_str, method):
        self.rules = copy.deepcopy(rules)
        self.gt = set(f.strip() for f in gt_str.split(',') if f.strip())
        self.kl_str = kl_str.strip()
        self.method = method
        
        self.summary_log = []
        self.vet = []
        self.linear_log = [] 
        self.step_counter = 0
        
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
        # ... (Giữ nguyên logic chọn luật và tính toán FPG) ...
        if not rule_indices:
            return [], ""
        if self.method == 'min':
            return sorted(rule_indices), ""
        if self.method == 'max':
            return sorted(rule_indices, reverse=True), ""
        if self.method == 'fpg':
            rule_heuristics = []
            log_details = "<div class='calc-box'>"
            log_details += "<b>Tính heuristic h(r):</b><br>" # Rút gọn tiêu đề
            for r_index in rule_indices:
                rule = self.rules[r_index]
                max_dist = 0
                details_per_premise = []
                for f in rule['left']:
                    dist = self.graph_builder.get_fpg_distance_to_gt(f, self.gt)
                    d_str = "∞" if dist == float('inf') else str(dist)
                    details_per_premise.append(f"d({f})={d_str}") # Rút gọn log
                    if dist == float('inf'):
                        max_dist = float('inf')
                        break
                    if dist > max_dist:
                        max_dist = dist
                
                h_val_str = "∞" if max_dist == float('inf') else str(max_dist)
                log_details += f"&nbsp;• r{r_index+1}: max({', '.join(details_per_premise)}) = <b>{h_val_str}</b><br>"
                rule_heuristics.append((r_index, max_dist))

            rule_heuristics.sort(key=lambda x: (x[1], x[0]))
            sorted_indices = [r_index for r_index, h_val in rule_heuristics]
            best_r = sorted_indices[0] + 1
            log_details += f"➔ <b>Chọn r{best_r}</b>"
            log_details += "</div>"
            return sorted_indices, log_details
        return sorted(rule_indices), ""

    # 🚩 [THAY ĐỔI LỚN] Hàm sinh HTML dạng Card thẳng hàng
    def _add_linear_step(self, logic_type, message, status='pending', calc_log=None, extra_info=None):
        """
        logic_type: Loại hành động (GOAL, CHECK, RULE, RESULT)
        """
        self.step_counter += 1
        
        # Màu sắc và Icon cho từng trạng thái
        status_class = "step-default"
        icon = "🔹"
        
        if status == 'proven':
            status_class = "step-success"
            icon = "✅"
        elif status == 'failed':
            status_class = "step-danger"
            icon = "❌"
        elif status == 'gt':
            status_class = "step-info"
            icon = "💎"
        elif status == 'loop':
            status_class = "step-warning"
            icon = "🔄"
        elif status == 'conclusion_success':
            status_class = "step-final-success"
            icon = "🏆"
        elif status == 'conclusion_failed':
            status_class = "step-final-failed"
            icon = "⛔"
            
        # Nhãn logic (Badge)
        logic_badge_color = "#6c757d"
        if logic_type == "GOAL": logic_badge_color = "#007bff"; # Xanh dương
        if logic_type == "CHECK": logic_badge_color = "#17a2b8"; # Xanh lơ
        if logic_type == "RULE": logic_badge_color = "#fd7e14"; # Cam
        if logic_type == "RESULT": logic_badge_color = "#28a745"; # Xanh lá
        
        badge_html = f'<span class="logic-badge" style="background-color: {logic_badge_color}">{logic_type}</span>'

        # Cấu trúc HTML mới: Dạng thẻ (Card)
        html = f"""
        <div class="log-step-card {status_class}">
            <div class="step-header">
                <span class="step-number">#{self.step_counter}</span>
                {badge_html}
                <span class="step-icon">{icon}</span>
            </div>
            <div class="step-content">
                <div class="step-message">{message}</div>
        """
        
        if extra_info:
             html += f"<div class='step-extra'>{extra_info}</div>"

        if calc_log:
            html += calc_log
            
        html += "</div></div>" # Đóng content và card
        self.linear_log.append(html)

    def _prove(self, goal, path, path_node_map, parent_node_id=None, depth=0):
        
        current_node_id = self.node_counter
        self.node_counter += 1
        graph_node_data = {'id': current_node_id, 'label': goal}
        if parent_node_id is not None:
            self.graph_edges.append({'from': current_node_id, 'to': parent_node_id})

        # 1. Check GT
        if goal in self.gt:
            graph_node_data['group'] = 'gt'
            self.graph_nodes.append(graph_node_data)
            self._add_linear_step("CHECK", f"Kiểm tra <b>{goal}</b>: Có trong Giả thiết.", 'gt')
            return {'status': 'gt'}
            
        # 2. Check Loop
        if goal in path:
            graph_node_data['group'] = 'loop'
            graph_node_data['label'] += ' (Lặp)'
            self.graph_nodes.append(graph_node_data)
            original_node_id = path_node_map[goal]
            self.graph_edges.append({'from': original_node_id, 'to': current_node_id, 'label': 'Quay lui', 'dashes': True})
            self._add_linear_step("CHECK", f"Kiểm tra <b>{goal}</b>: Phát hiện lặp. Quay lui.", 'loop')
            return {'status': 'loop'}
            
        self.graph_nodes.append(graph_node_data)
        path_node_map[goal] = current_node_id

        # 3. Tìm luật
        applicable_rule_indices = self._find_rules_for_goal(goal)
        if not applicable_rule_indices:
            graph_node_data['group'] = 'failed'
            self._add_linear_step("GOAL", f"Cần chứng minh <b>{goal}</b>. Không tìm thấy luật nào sinh ra nó.", 'failed')
            return {'status': 'failed'}
            
        thoa, calc_log = self._select_rules(applicable_rule_indices)
        
        thoa_str = "{" + self._format_list([i+1 for i in thoa]) + "}"
        
        # Ghi log bắt đầu xử lý mục tiêu
        self._add_linear_step("GOAL", f"Cần chứng minh <b>{goal}</b>.", 'pending', calc_log, f"Luật khả dụng (THOA): {thoa_str}")
        
        # 4. Thử luật
        for r_index in thoa:
            rule = self.rules[r_index]
            
            self._add_linear_step("RULE", f"Áp dụng <b>Luật r{r_index+1}</b>: {rule['raw_left']} -> {rule['right']}", 'pending')
            
            rule_node_id = self.node_counter
            self.node_counter += 1
            premise_label = ','.join(sorted(list(rule['left'])))
            rule_graph_node_data = {'id': rule_node_id, 'label': f'{{{premise_label}}} (r{r_index+1})', 'shape': 'box'}
            self.graph_nodes.append(rule_graph_node_data)
            self.graph_edges.append({'from': rule_node_id, 'to': current_node_id})

            all_premises_proven = True
            premises = sorted(list(rule['left']))
            
            # Chứng minh từng tiền đề
            for premise in premises:
                res = self._prove(premise, path + [goal], path_node_map.copy(), rule_node_id, depth + 1)
                
                if res['status'] not in ['proven', 'gt']:
                    all_premises_proven = False
                    rule_graph_node_data['group'] = 'failed'
                    break 
            
            if all_premises_proven:
                self.vet.append(r_index + 1)
                graph_node_data['group'] = 'proven'
                rule_graph_node_data['group'] = 'proven'
                
                # Thành công
                new_vet_str = "{" + self._format_list(self.vet) + "}"
                self._add_linear_step("RESULT", f"<b>Luật r{r_index+1} thành công</b>. Suy ra được <b>{goal}</b>.", 'proven', None, f"Cập nhật VET: {new_vet_str}")
                return {'status': 'proven'} 
            else:
                # Thất bại luật này -> Thử luật tiếp theo
                pass
                
        # Nếu chạy hết vòng lặp mà không return -> Thất bại mục tiêu
        graph_node_data['group'] = 'failed'
        self._add_linear_step("RESULT", f"Thất bại chứng minh <b>{goal}</b> (đã thử hết luật).", 'failed')
        return {'status': 'failed'}

    def run(self):
        if not self.kl_str:
            return {'status': 'Lỗi', 'summary_log': ['Vui lòng nhập mục tiêu']}
            
        self.graph_nodes = []
        self.graph_edges = []
        self.node_counter = 0
        self.summary_log = []
        self.linear_log = [] 
        self.step_counter = 0
        self.vet = []
            
        # Phần tóm tắt đầu vào
        self.summary_log.append(f"Mục tiêu: {self.kl_str}")
        self.summary_log.append(f"Giả thiết: {{{self._format_set(self.gt)}}}")
        
        result_dict = self._prove(self.kl_str, [], {}, depth=0)
        
        is_proven = result_dict['status'] in ['proven', 'gt']
        
        # Log kết luận cuối cùng
        final_vet_str = "{" + self._format_list(self.vet) + "}" # VET suy diễn ngược
        if is_proven:
            self.vet.reverse() # VET suy diễn xuôi
            final_vet_display = "{" + self._format_list(self.vet) + "}"
            msg = f"<b>THÀNH CÔNG!</b> Mục tiêu {self.kl_str} đã được chứng minh."
            self._add_linear_step("FINISH", msg, 'conclusion_success', None, f"<b>VET (Xuôi)</b> = {final_vet_display}")
            result = "Thành công"
        else:
            msg = f"<b>THẤT BẠI!</b> Không thể chứng minh mục tiêu {self.kl_str}."
            self._add_linear_step("FINISH", msg, 'conclusion_failed', None, f"VET = {final_vet_str}")
            result = "Thất bại"
            
        fpg_static_data = None
        if self.method == 'fpg' and self.graph_builder:
            fpg_static_data = self.graph_builder.build_fpg_data(self.gt, {self.kl_str})

        return {
            'status': result, 
            'summary_log': self.summary_log,
            'linear_log': self.linear_log, 
            'vet': self.vet,
            'graph_data': {'nodes': self.graph_nodes, 'edges': self.graph_edges},
            'fpg_data': fpg_static_data
        }