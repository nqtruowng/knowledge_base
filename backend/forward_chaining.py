from graph_builder import GraphBuilder
import copy

class ForwardChainer:
    def __init__(self, rules, gt_str, kl_str, method):
        self.rules = copy.deepcopy(rules) # List dạng [{'left': {'a', 'b'}, 'right': 'c'}, ...]
        self.gt = set(f.strip() for f in gt_str.split(',') if f.strip())
        self.kl = set(f.strip() for f in kl_str.split(',') if f.strip())
        self.method = method # 'stack', 'queue', 'min', 'max', 'fpg', 'rpg'
        
        self.tg = set(self.gt) # TG (Tập trung gian)
        self.vet = []          # VET (Vết suy diễn - 1-based index)
        self.r_used_indices = set() # Các luật đã dùng (theo index 0-based)
        self.log = []          # Log các bước
        
        # 🚩 THÊM MỚI (YÊU CẦU 3.2): Bảng tóm tắt các bước
        self.trace_table = []
        
        self.graph_builder = None
        self.rkl_indices = None
        if self.method in ['fpg', 'rpg']:
            self.graph_builder = GraphBuilder(self.rules)
            if self.method == 'rpg':
                # Tìm RKL (tập luật thỏa mãn kết luận)
                self.rkl_indices = {i for i, r in enumerate(self.rules) if r['right'] in self.kl}


    def _format_set(self, s):
        """Helper: Định dạng set thành chuỗi 'a,b,c'."""
        return ','.join(sorted(list(s)))

    def _format_list(self, l):
        """Helper: Định dạng list thành chuỗi '1,2,3'."""
        return ','.join(map(str, l))

    def _get_r_remaining_str(self):
        """Helper: Lấy danh sách (str) các luật (1-based) CHƯA SỬ DỤNG."""
        remaining = [i + 1 for i in range(len(self.rules)) if i not in self.r_used_indices]
        return self._format_list(sorted(remaining))

    def _loc(self):
        """Hàm LOC(TG, R) - Tìm các luật thỏa mãn."""
        satisfied_rules = []
        for i, rule in enumerate(self.rules):
            if i not in self.r_used_indices and rule['left'].issubset(self.tg):
                satisfied_rules.append(i)
        return satisfied_rules

    def _select_rule_from_thoa(self, thoa):
        """Chọn luật từ THOA dựa trên phương pháp."""
        if not thoa:
            return None
        
        if self.method == 'stack':
            return thoa.pop() # Lấy cuối (LIFO)
        if self.method == 'queue':
            return thoa.pop(0) # Lấy đầu (FIFO)
        if self.method == 'min':
            selected = min(thoa)
            thoa.remove(selected)
            return selected
        if self.method == 'max':
            selected = max(thoa)
            thoa.remove(selected)
            return selected
        
        if self.method == 'fpg':
            # Tính h(r) = KC(q, KL) cho mọi r trong THOA
            best_rule = -1
            min_h = float('inf')
            
            for r_index in thoa:
                q = self.rules[r_index]['right']
                h = self.graph_builder.get_fpg_distance(q, self.kl)
                
                if h < min_h:
                    min_h = h
                    best_rule = r_index
                elif h == min_h:
                    # Nếu h bằng nhau, ưu tiên chỉ số nhỏ nhất (theo slide)
                    if best_rule == -1 or r_index < best_rule:
                        best_rule = r_index
                        
            if best_rule != -1:
                thoa.remove(best_rule)
                return best_rule
            else: # Không có luật nào đến được KL
                return thoa.pop(0) # Quay về FIFO

        if self.method == 'rpg':
            # Tính h(r) = KC(r, RKL) cho mọi r trong THOA
            best_rule = -1
            min_h = float('inf')

            for r_index in thoa:
                h = self.graph_builder.get_rpg_distance(r_index, self.rkl_indices)
                
                if h < min_h:
                    min_h = h
                    best_rule = r_index
                elif h == min_h:
                    if best_rule == -1 or r_index < best_rule:
                        best_rule = r_index

            if best_rule != -1:
                thoa.remove(best_rule)
                return best_rule
            else: # Không có luật nào đến được RKL
                return thoa.pop(0) # Quay về FIFO

        return None # Mặc định

    def run(self):
        """Thực thi thuật toán suy diễn tiến."""
        
        # Bước 1: Khởi tạo
        thoa_indices = self._loc() # Tìm các luật thỏa mãn ban đầu
        
        # Cần một list THOA có thể pop/remove (không phải set)
        if self.method in ['stack', 'max']:
             thoa = sorted(thoa_indices) # Stack/Max ưu tiên chỉ số cao
        else:
             thoa = sorted(thoa_indices) # Queue/Min ưu tiên chỉ số thấp
        
        self.log.append(f"Khởi tạo: TG = {{{self._format_set(self.tg)}}}, VET = {{}}, THOA = {{{self._format_list([i+1 for i in thoa])}}}")
        
        # 🚩 THÊM MỚI (YÊU CẦU 3.2): Thêm trạng thái khởi tạo vào bảng
        self.trace_table.append({
            'r': '',
            'thoa': self._format_list([i+1 for i in thoa]),
            'tg': self._format_set(self.tg),
            'r_remaining': self._get_r_remaining_str(),
            'vet': self._format_list(self.vet)
        })
        
        step_count = 1
        
        # Bước 2: Lặp
        # Dừng khi THOA rỗng HOẶC (có KL và KL đã nằm trong TG)
        while thoa and (not self.kl or not self.kl.issubset(self.tg)):
            
            # 2.1. Chọn luật r
            r_index = self._select_rule_from_thoa(thoa)
            if r_index is None:
                break
                
            rule = self.rules[r_index]
            q = rule['right']
            
            # 2.2. Cập nhật VET và R
            self.vet.append(r_index + 1) # Dùng 1-based index
            self.r_used_indices.add(r_index)
            
            # Log bước chọn luật
            log_entry = f"Bước {step_count}: Chọn luật r{r_index + 1}. "
            
            # 2.3. Cập nhật TG
            if q not in self.tg:
                self.tg.add(q)
                log_entry += f"Thêm {q} vào TG. "
                
                # 2.4. Cập nhật THOA (Tìm các luật *mới* thỏa mãn)
                newly_satisfied = self._loc() # Tìm tất cả luật thỏa mãn (bao gồm cả cũ)
                
                new_indices_to_add = []
                for new_idx in newly_satisfied:
                    if new_idx not in thoa: # Chỉ thêm nếu chưa có trong THOA
                        new_indices_to_add.append(new_idx)
                
                # Thêm vào THOA theo logic Stack/Queue
                if new_indices_to_add:
                    new_indices_to_add.sort() # Sắp xếp để thêm theo thứ tự
                    if self.method == 'stack':
                         thoa.extend(new_indices_to_add) # Thêm vào cuối (LIFO)
                    else: # Queue, Min, Max, FPG, RPG
                         thoa.extend(new_indices_to_add) # Thêm vào cuối (FIFO)
                         if self.method in ['min', 'max']:
                             thoa.sort() # Sắp xếp lại để min/max hoạt động
                         
            else:
                 log_entry += f"Sự kiện {q} đã có trong TG. "

            log_entry += f"TG = {{{self._format_set(self.tg)}}}, VET = {{{self._format_list(self.vet)}}}, THOA = {{{self._format_list([i+1 for i in thoa])}}}"
            self.log.append(log_entry)
            
            # 🚩 THÊM MỚI (YÊU CẦU 3.2): Thêm trạng thái bước này vào bảng
            self.trace_table.append({
                'r': str(r_index + 1),
                'thoa': self._format_list([i+1 for i in thoa]),
                'tg': self._format_set(self.tg),
                'r_remaining': self._get_r_remaining_str(),
                'vet': self._format_list(self.vet)
            })
            
            step_count += 1

        # Bước 3: Kết luận
        if self.kl:
            if self.kl.issubset(self.tg):
                result = "Thành công"
                self.log.append(f"Kết thúc: {result}. KL = {{{self._format_set(self.kl)}}} đã được suy diễn.")
            else:
                result = "Thất bại"
                self.log.append(f"Kết thúc: {result}. Không thể suy diễn KL = {{{self._format_set(self.kl)}}}.")
        else:
            result = "Hoàn thành"
            self.log.append(f"Kết thúc: Đã suy diễn tất cả sự kiện có thể.")
            
        # 🚩 SỬA LỖI (YÊU CẦU 3.2): Trả về trace_table
        return {
            'status': result, 
            'log': self.log, 
            'vet': self.vet, 
            'tg': list(self.tg), 
            'trace_table': self.trace_table 
        }