from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import io
from knowledge_base import KnowledgeBase
from graph_builder import GraphBuilder
from forward_chaining import ForwardChainer
from backward_chaining import BackwardChainer

app = Flask(__name__)
CORS(app)  # Cho phép frontend gọi API

# Khởi tạo một cơ sở tri thức (KB) toàn cục
kb = KnowledgeBase()

# --- 1. API QUẢN LÝ LUẬT ---

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Lấy tất cả luật hiện có."""
    return jsonify(kb.get_all_rules_serializable())

@app.route('/api/rules', methods=['POST'])
def add_rule():
    """Thêm một luật mới."""
    data = request.json
    try:
        index = kb.add_rule(data['left'], data['right'])
        return jsonify({'status': 'success', 'index': index}), 201
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/rules/<int:index>', methods=['PUT'])
def update_rule(index):
    """Cập nhật luật theo vị trí (index)."""
    data = request.json
    try:
        kb.update_rule(index, data['left'], data['right'])
        return jsonify({'status': 'success'})
    except (IndexError, ValueError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/rules/<int:index>', methods=['DELETE'])
def delete_rule(index):
    """Xóa luật theo vị trí (index)."""
    try:
        kb.delete_rule(index)
        return jsonify({'status': 'success'})
    except IndexError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/import_csv', methods=['POST'])
def import_csv():
    """Nhập luật từ file CSV."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    try:
        # Đọc nội dung file từ memory
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.reader(stream)
        
        new_rules = []
        for row in csv_reader:
            if row:
                line = row[0] # Giả sử CSV chỉ có 1 cột 'a^b -> c'
                if '->' in line:
                    parts = line.split('->')
                    if len(parts) == 2:
                        left, right = parts[0].strip(), parts[1].strip()
                        index = kb.add_rule(left, right)
                        
                        # --- SỬA LỖI TẠI ĐÂY ---
                        # Lấy luật vừa thêm từ KB
                        rule_data = kb.rules[index]
                        # Tạo một đối tượng an toàn cho JSON
                        serializable_rule = {
                            'index': index,
                            'left': rule_data['raw_left'],
                            'right': rule_data['raw_right']
                        }
                        new_rules.append(serializable_rule)
                        # ---------------------
                        
        return jsonify({'status': 'success', 'new_rules': new_rules})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error processing file: {e}'}), 500

# --- 2. API VẼ ĐỒ THỊ ---

def get_graph_builder():
    """Hàm trợ giúp lấy luật và tạo GraphBuilder."""
    rules = kb.get_rules_for_chaining()
    return GraphBuilder(rules)

@app.route('/api/fpg', methods=['POST'])
def get_fpg_graph():
    """Lấy dữ liệu đồ thị FPG."""
    data = request.json
    gt = set(f.strip() for f in data.get('gt', '').split(',') if f.strip())
    kl = set(f.strip() for f in data.get('kl', '').split(',') if f.strip())
    
    builder = get_graph_builder()
    graph_data = builder.build_fpg_data(gt, kl)
    return jsonify(graph_data)

@app.route('/api/rpg', methods=['POST'])
def get_rpg_graph():
    """Lấy dữ liệu đồ thị RPG."""
    data = request.json
    gt = set(f.strip() for f in data.get('gt', '').split(',') if f.strip())
    kl = set(f.strip() for f in data.get('kl', '').split(',') if f.strip())
    
    builder = get_graph_builder()
    graph_data = builder.build_rpg_data(gt, kl)
    return jsonify(graph_data)

# --- 3. API SUY DIỄN TIẾN ---

@app.route('/api/forward', methods=['POST'])
def run_forward_chaining():
    data = request.json
    rules = kb.get_rules_for_chaining()
    gt = data.get('facts', '')
    kl = data.get('goal', '')
    method = data.get('method', 'stack')
    
    try:
        chainer = ForwardChainer(rules, gt, kl, method)
        result = chainer.run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'log': [f'Lỗi server: {e}']}), 500

# --- 4. API SUY DIỄN LÙI ---

@app.route('/api/backward', methods=['POST'])
def run_backward_chaining():
    data = request.json
    rules = kb.get_rules_for_chaining()
    gt = data.get('facts', '')
    kl = data.get('goal', '')
    method = data.get('method', 'min') # Mặc định là min nếu không chọn
    
    try:
        chainer = BackwardChainer(rules, gt, kl, method)
        result = chainer.run()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'log': [f'Lỗi server: {e}']}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001) # Chạy trên cổng 5001