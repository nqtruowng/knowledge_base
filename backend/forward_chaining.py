from graph_builder import GraphBuilder
import copy

class ForwardChainer:
    def __init__(self, rules, gt_str, kl_str, method):
        self.rules = copy.deepcopy(rules)
        self.gt = set(f.strip() for f in gt_str.split(',') if f.strip())
        self.kl = set(f.strip() for f in kl_str.split(',') if f.strip())
        self.method = method 
        
        self.tg = set(self.gt) 
        self.vet = []          
        self.r_used_indices = set() 
        self.log = []          
        self.trace_table = []
        
        self.graph_builder = None
        self.rkl_indices = None
        
        # Chuẩn bị GraphBuilder nếu cần
        if self.method in ['fpg', 'rpg']:
            self.graph_builder = GraphBuilder(self.rules)
            if self.method == 'rpg':
                self.rkl_indices = {i for i, r in enumerate(self.rules) if r['right'] in self.kl}

    def _format_set(self, s):
        return ','.join(sorted(list(s)))

    def _format_list(self, l):
        return ','.join(map(str, l))

    def _get_r_remaining_str(self):
        remaining = [i + 1 for i in range(len(self.rules)) if i not in self.r_used_indices]
        return self._format_list(sorted(remaining))

    def _loc(self):
        satisfied_rules = []
        for i, rule in enumerate(self.rules):
            if i not in self.r_used_indices and rule['left'].issubset(self.tg):
                satisfied_rules.append(i)
        return satisfied_rules

    def _select_rule_from_thoa(self, thoa):
        """
        Trả về: (selected_index, calculation_log_html)
        """
        if not thoa:
            return None, ""
        
        # --- Các phương pháp cơ bản (giữ nguyên) ---
        if self.method == 'stack':
            return thoa.pop(), "" 
        if self.method == 'queue':
            return thoa.pop(0), ""
        if self.method == 'min':
            selected = min(thoa)
            thoa.remove(selected)
            return selected, ""
        if self.method == 'max':
            selected = max(thoa)
            thoa.remove(selected)
            return selected, ""
        
        # --- Phương pháp FPG ---
        if self.method == 'fpg':
            calc_log = "<div class='calc-box'>"
            calc_log += "<b>Tính hàm lượng giá h (Khoảng cách đến KL):</b><br>"
            
            best_rule = -1
            min_h = float('inf')
            
            heuristics = []

            for r_index in thoa:
                q = self.rules[r_index]['right']
                # Tính khoảng cách từ sự kiện đích của luật đến KL
                h = self.graph_builder.get_fpg_distance(q, self.kl)
                
                h_str = "∞" if h == float('inf') else str(h)
                heuristics.append({'r': r_index, 'h': h, 'q': q})
                
                calc_log += f"&nbsp;&nbsp;• <i>h(r{r_index+1})</i> = KC({q}, KL) = <b>{h_str}</b><br>"

                if h < min_h:
                    min_h = h
                    best_rule = r_index
                elif h == min_h:
                    if best_rule == -1 or r_index < best_rule:
                        best_rule = r_index
            
            calc_log += f"➔ Chọn luật <b>r{best_rule+1}</b> vì h nhỏ nhất."
            calc_log += "</div>"

            if best_rule != -1:
                thoa.remove(best_rule)
                return best_rule, calc_log
            else:
                # Fallback nếu không tìm thấy đường đi
                fallback = thoa.pop(0)
                return fallback, calc_log + "<br>(Không tìm thấy đường đi, chọn theo Queue)"

        # --- Phương pháp RPG ---
        if self.method == 'rpg':
            calc_log = "<div class='calc-box'>"
            calc_log += "<b>Tính hàm lượng giá h (KC trên đồ thị luật):</b><br>"
            
            best_rule = -1
            min_h = float('inf')

            for r_index in thoa:
                # Tính khoảng cách từ luật hiện tại đến tập luật đích RKL
                h = self.graph_builder.get_rpg_distance(r_index, self.rkl_indices)
                
                h_str = "∞" if h == float('inf') else str(h)
                calc_log += f"&nbsp;&nbsp;• <i>h(r{r_index+1})</i> = KC(r{r_index+1}, RKL) = <b>{h_str}</b><br>"
                
                if h < min_h:
                    min_h = h
                    best_rule = r_index
                elif h == min_h:
                    if best_rule == -1 or r_index < best_rule:
                        best_rule = r_index

            calc_log += f"➔ Chọn luật <b>r{best_rule+1}</b> vì h nhỏ nhất."
            calc_log += "</div>"

            if best_rule != -1:
                thoa.remove(best_rule)
                return best_rule, calc_log
            else:
                fallback = thoa.pop(0)
                return fallback, calc_log + "<br>(Không tìm thấy đường đi, chọn theo Queue)"

        return None, ""

    def run(self):
        """Thực thi thuật toán suy diễn tiến."""
        
        # Bước 1: Khởi tạo
        thoa_indices = self._loc()
        
        if self.method in ['stack', 'max']:
             thoa = sorted(thoa_indices)
        else:
             thoa = sorted(thoa_indices)
        
        self.log.append(f"<b>Khởi tạo:</b><br>TG = {{{self._format_set(self.tg)}}}<br>THOA = {{{self._format_list([i+1 for i in thoa])}}}")
        
        self.trace_table.append({
            'r': '',
            'thoa': self._format_list([i+1 for i in thoa]),
            'tg': self._format_set(self.tg),
            'r_remaining': self._get_r_remaining_str(),
            'vet': self._format_list(self.vet)
        })
        
        step_count = 1
        
        while thoa and (not self.kl or not self.kl.issubset(self.tg)):
            
            # 2.1. Chọn luật r (kèm log tính toán)
            r_index, calc_log = self._select_rule_from_thoa(thoa)
            
            if r_index is None:
                break
                
            rule = self.rules[r_index]
            q = rule['right']
            
            self.vet.append(r_index + 1)
            self.r_used_indices.add(r_index)
            
            # Tạo nội dung log cho bước này
            step_html = f"<hr><b>Bước {step_count}:</b><br>"
            
            # Chèn log tính toán (nếu có - FPG/RPG)
            if calc_log:
                step_html += calc_log
            
            step_html += f"Chọn luật <b>r{r_index + 1}</b> ({rule['raw_left']} -> {rule['right']}).<br>"
            
            if q not in self.tg:
                self.tg.add(q)
                step_html += f"Thêm <b>{q}</b> vào TG.<br>"
                
                newly_satisfied = self._loc()
                new_indices_to_add = []
                for new_idx in newly_satisfied:
                    if new_idx not in thoa:
                        new_indices_to_add.append(new_idx)
                
                if new_indices_to_add:
                    new_indices_to_add.sort()
                    if self.method == 'stack':
                         thoa.extend(new_indices_to_add)
                    else: 
                         thoa.extend(new_indices_to_add)
                         if self.method in ['min', 'max']:
                             thoa.sort()
            else:
                 step_html += f"Sự kiện {q} đã có trong TG. "

            step_html += f"TG = {{{self._format_set(self.tg)}}}<br>VET = {{{self._format_list(self.vet)}}}<br>THOA = {{{self._format_list([i+1 for i in thoa])}}}"
            
            self.log.append(step_html)
            
            self.trace_table.append({
                'r': str(r_index + 1),
                'thoa': self._format_list([i+1 for i in thoa]),
                'tg': self._format_set(self.tg),
                'r_remaining': self._get_r_remaining_str(),
                'vet': self._format_list(self.vet)
            })
            
            step_count += 1

        # Bước 3: Kết luận
        final_log = "<hr><b>Kết thúc:</b> "
        if self.kl:
            if self.kl.issubset(self.tg):
                result = "Thành công"
                final_log += f"<span style='color:green'>Thành công</span>. KL đã được chứng minh."
            else:
                result = "Thất bại"
                final_log += f"<span style='color:red'>Thất bại</span>. Không thể suy diễn đủ KL."
        else:
            result = "Hoàn thành"
            final_log += "Đã suy diễn tất cả sự kiện có thể."
        
        self.log.append(final_log)
        
        # Lấy dữ liệu đồ thị tĩnh để vẽ (nếu method là fpg/rpg)
        static_graph_data = None
        if self.method == 'fpg' and self.graph_builder:
            static_graph_data = self.graph_builder.build_fpg_data(self.gt, self.kl)
        elif self.method == 'rpg' and self.graph_builder:
            static_graph_data = self.graph_builder.build_rpg_data(self.gt, self.kl)

        return {
            'status': result, 
            'log': self.log, 
            'vet': self.vet, 
            'tg': list(self.tg), 
            'trace_table': self.trace_table,
            'graph_data': static_graph_data # Dữ liệu để vẽ bên phải
        }