class KnowledgeBase:
    """Quản lý tập luật R."""
    def __init__(self):
        self.rules = [] # List lưu các luật gốc, dạng {'raw_left': 'a^b', 'raw_right': 'c', 'left': {'a', 'b'}, 'right': 'c'}

    def _parse_rule(self, left_str, right_str):
        """Phân tích chuỗi luật thành các thành phần."""
        if not left_str or not right_str:
            raise ValueError("Vế trái và vế phải không được rỗng.")
        
        left_facts = set(f.strip() for f in left_str.split('^') if f.strip())
        right_fact = right_str.strip()
        
        if not left_facts:
             raise ValueError("Vế trái phải chứa ít nhất một sự kiện.")
        if len(right_fact.split()) > 1 or '^' in right_fact or ',' in right_fact:
             raise ValueError("Vế phải chỉ được chứa một sự kiện duy nhất.")
             
        return {
            'raw_left': left_str,
            'raw_right': right_str,
            'left': left_facts,
            'right': right_fact
        }

    def add_rule(self, left_str, right_str):
        """Thêm luật mới và trả về index của nó."""
        rule_data = self._parse_rule(left_str, right_str)
        self.rules.append(rule_data)
        return len(self.rules) - 1 # Trả về index vừa thêm

    def update_rule(self, index, left_str, right_str):
        """Cập nhật luật tại index."""
        if 0 <= index < len(self.rules):
            rule_data = self._parse_rule(left_str, right_str)
            self.rules[index] = rule_data
        else:
            raise IndexError("Không tìm thấy luật để cập nhật.")

    def delete_rule(self, index):
        """Xóa luật tại index."""
        if 0 <= index < len(self.rules):
            self.rules.pop(index)
        else:
            raise IndexError("Không tìm thấy luật để xóa.")

    def get_all_rules_serializable(self):
        """Lấy tất cả luật ở định dạng có thể gửi qua JSON."""
        # Trả về index (hàng trong table) và luật
        return [
            {'index': i, 'left': rule['raw_left'], 'right': rule['raw_right']}
            for i, rule in enumerate(self.rules)
        ]
        
    def get_rules_for_chaining(self):
        """
        Lấy danh sách luật đã được phân tích cho các thuật toán suy diễn.
        """
        # --- 🚩 SỬA LỖI TẠI ĐÂY ---
        # Trả về MỘT BẢN SAO của danh sách luật đầy đủ.
        # Các Chainer/Builder sẽ nhận đầy đủ {'left', 'right', 'raw_left', 'raw_right'}
        # (Hàm .copy() tạo một bản sao nông (shallow copy) của dict)
        return [rule.copy() for rule in self.rules]
        # ------------------------