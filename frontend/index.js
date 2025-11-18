// Khai báo API endpoint
const API_URL = "http://127.0.0.1:5001"; // Port của server Flask

const methodExplanations = {
  forward: {
    stack: `
      <h3>Chiến lược Stack (Ngăn xếp - DFS)</h3>
      <p><b>Nguyên lý:</b> Last In, First Out (Vào sau, Ra trước).</p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Khi tập <b>THOA</b> (các luật thỏa mãn) có nhiều luật, thuật toán sẽ chọn luật <b>mới nhất</b> vừa được thêm vào.</li>
        <li>Nếu xét theo danh sách, nó sẽ lấy phần tử ở <b>cuối cùng</b> của danh sách THOA.</li>
      </ul>
      <p><i>Ví dụ: THOA = {r1, r2}. Tìm thấy r3 thỏa mãn -> THOA = {r1, r2, r3}. Chọn r3.</i></p>
    `,
    queue: `
      <h3>Chiến lược Queue (Hàng đợi - BFS)</h3>
      <p><b>Nguyên lý:</b> First In, First Out (Vào trước, Ra trước).</p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Thuật toán sẽ chọn luật <b>cũ nhất</b> (luật đã nằm trong THOA lâu nhất).</li>
        <li>Nếu xét theo danh sách, nó sẽ lấy phần tử ở <b>đầu tiên</b> của danh sách THOA.</li>
      </ul>
      <p><i>Ví dụ: THOA = {r1, r2}. Chọn r1.</i></p>
    `,
    min: `
      <h3>Chiến lược Chỉ số Min</h3>
      <p><b>Nguyên lý:</b> Ưu tiên thứ tự luật trong cơ sở tri thức.</p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Trong tập <b>THOA</b>, chọn luật có <b>chỉ số nhỏ nhất</b> (xuất hiện sớm nhất trong danh sách luật ban đầu).</li>
      </ul>
    `,
    max: `
      <h3>Chiến lược Chỉ số Max</h3>
      <p><b>Nguyên lý:</b> Ưu tiên thứ tự luật trong cơ sở tri thức (ngược).</p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Trong tập <b>THOA</b>, chọn luật có <b>chỉ số lớn nhất</b>.</li>
      </ul>
    `,
    fpg: `
      <h3>Chiến lược FPG (Facts Precedence Graph)</h3>
      <p><b>Nguyên lý:</b> Heuristic dựa trên khoảng cách sự kiện.</p>
      <p><b>Công thức:</b> <code>h(r) = KC(Vế_Phải(r), Tập_KL)</code></p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Với mỗi luật trong THOA, tính khoảng cách ngắn nhất trên đồ thị FPG từ sự kiện sinh ra (vế phải) đến sự kiện đích (KL).</li>
        <li>Chọn luật có khoảng cách <b>h nhỏ nhất</b> (gần đích nhất).</li>
      </ul>
    `,
    rpg: `
      <h3>Chiến lược RPG (Rules Precedence Graph)</h3>
      <p><b>Nguyên lý:</b> Heuristic dựa trên khoảng cách giữa các luật.</p>
      <p><b>Công thức:</b> <code>h(r) = KC(r, Tập_Luật_Đích_RKL)</code></p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Tính khoảng cách trên đồ thị RPG từ luật hiện tại đến tập các luật sinh ra kết luận (RKL).</li>
        <li>Chọn luật có <b>h nhỏ nhất</b>.</li>
      </ul>
    `
  },
  backward: {
    min: `
      <h3>Chiến lược Chỉ số Min (Suy diễn lùi)</h3>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Khi có nhiều luật cùng sinh ra mục tiêu hiện tại, chọn luật có <b>chỉ số nhỏ nhất</b> để thử trước.</li>
        <li>Đây là chiến lược tìm kiếm mù quáng (Blind Search).</li>
      </ul>
    `,
    max: `
      <h3>Chiến lược Chỉ số Max (Suy diễn lùi)</h3>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Khi có nhiều luật cùng sinh ra mục tiêu hiện tại, chọn luật có <b>chỉ số lớn nhất</b> để thử trước.</li>
      </ul>
    `,
    fpg: `
      <h3>Chiến lược FPG (Suy diễn lùi)</h3>
      <p><b>Nguyên lý:</b> Chọn luật có tiền đề dễ chứng minh nhất (gần GT nhất).</p>
      <p><b>Công thức:</b> <code>h(r) = MAX( KC(Tiền_đề_i, Tập_GT) )</code></p>
      <p><b>Cách chọn luật:</b></p>
      <ul>
        <li>Với mỗi luật có thể sinh ra mục tiêu, xét tất cả các sự kiện ở vế trái (tiền đề).</li>
        <li>Tính khoảng cách từ sự kiện đó về Giả thiết (GT).</li>
        <li>Chọn luật mà các tiền đề của nó <b>gần GT nhất</b> (h nhỏ nhất).</li>
      </ul>
    `
  }
};

// --- HÀM HIỂN THỊ MODAL HƯỚNG DẪN ---
function showMethodGuide(type, method) {
  const content = methodExplanations[type][method];
  if (content) {
    document.getElementById("helpModalTitle").textContent = "Hướng dẫn cách làm";
    document.getElementById("helpModalBody").innerHTML = content;
    document.getElementById("helpModal").style.display = "flex";
  }
}

// --- HÀM TẠO BUTTON HƯỚNG DẪN ---
function createGuideButton(type, method) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn-guide-how-to"; // Class CSS mới
  btn.innerHTML = '<i class="fas fa-book-open"></i> Hướng dẫn cách làm';
  btn.onclick = () => showMethodGuide(type, method);
  return btn;
}



document.addEventListener("DOMContentLoaded", function () {
  // --- 1. XỬ LÝ CHUYỂN TAB (VIEW) ---
  const navItems = document.querySelectorAll(".sidebar-nav-item");
  const views = document.querySelectorAll(".view");

  navItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();
      navItems.forEach((nav) => nav.classList.remove("active"));
      this.classList.add("active");
      const targetId = this.getAttribute("data-target");
      views.forEach((view) => view.classList.remove("active"));
      document.getElementById(targetId).classList.add("active");
    });
  });

  // --- 2. XỬ LÝ IMPORT CSV ---
  const csvFileInput = document.getElementById("csvFileInput");
  csvFileInput.addEventListener("change", handleFileSelect);

  // --- 3. XỬ LÝ FORM TRONG MODAL ---
  const ruleForm = document.getElementById("ruleForm");
  ruleForm.addEventListener("submit", handleFormSubmit);

  // --- 4. TẢI LUẬT KHI MỞ TRANG ---
  loadRulesFromAPI();

  // --- 5. XỬ LÝ VẼ ĐỒ THỊ ---
  document.getElementById("btn-draw-fpg").addEventListener("click", drawFPG);
  document.getElementById("btn-draw-rpg").addEventListener("click", drawRPG);

  // --- 6. XỬ LÝ SUY DIỄN ---
  document
    .getElementById("form-forward")
    .addEventListener("submit", runForwardChaining);
  document
    .getElementById("form-backward")
    .addEventListener("submit", runBackwardChaining);
});

// --- HÀM CHO CHỨC NĂNG IMPORT CSV ---
function triggerCsvImport() {
  document.getElementById("csvFileInput").click();
}

async function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_URL}/api/import_csv`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (data.status === "success" && data.new_rules) {
      data.new_rules.forEach((rule) => {
        addRuleToTable(rule.left, rule.right, rule.index);
      });
      alert("Import thành công!");
    } else {
      alert("Lỗi khi import: " + data.message);
    }
  } catch (error) {
    console.error("Error importing CSV:", error);
    alert("Lỗi kết nối khi import CSV.");
  }
  event.target.value = null; // Reset input file
}

// --- CÁC HÀM XỬ LÝ MODAL (POP-UP) ---
const modal = document.getElementById("ruleModal");
const modalTitle = document.getElementById("modalTitle");
const modalRuleIndex = document.getElementById("modalRuleIndex");
const modalVeTrai = document.getElementById("modalVeTrai");
const modalVePhai = document.getElementById("modalVePhai");

function showModal(mode, rowIndex = null) {
  if (mode === "add") {
    modalTitle.textContent = "Thêm luật mới";
    modalRuleIndex.value = "";
    modalVeTrai.value = "";
    modalVePhai.value = "";
  } else if (mode === "edit") {
    modalTitle.textContent = "Sửa luật";
    modalRuleIndex.value = rowIndex;
    const row = tableBody.querySelector(`tr[data-index="${rowIndex}"]`);
    if (row) {
      modalVeTrai.value = row.cells[0].textContent;
      modalVePhai.value = row.cells[1].textContent;
    } else {
      alert("Lỗi: Không tìm thấy luật để sửa.");
      return;
    }
  }
  modal.style.display = "flex";
}

function hideModal() {
  modal.style.display = "none";
}

async function handleFormSubmit(event) {
  event.preventDefault();
  const veTrai = modalVeTrai.value.trim();
  const vePhai = modalVePhai.value.trim();
  const ruleIndex = modalRuleIndex.value;

  if (veTrai === "" || vePhai === "") {
    alert("Vui lòng nhập đầy đủ cả hai vế.");
    return;
  }

  if (ruleIndex) {
    // --- CHẾ ĐỘ SỬA (UPDATE) ---
    try {
      const response = await fetch(`${API_URL}/api/rules/${ruleIndex}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left: veTrai, right: vePhai }),
      });
      const data = await response.json();
      if (data.status === "success") {
        updateRuleInTable(ruleIndex, veTrai, vePhai);
        hideModal();
      } else {
        alert("Lỗi khi cập nhật luật: " + data.message);
      }
    } catch (error) {
      console.error("Error updating rule:", error);
      alert("Lỗi kết nối khi cập nhật luật.");
    }
  } else {
    // --- CHẾ ĐỘ THÊM (ADD) ---
    try {
      const response = await fetch(`${API_URL}/api/rules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left: veTrai, right: vePhai }),
      });
      const data = await response.json();
      if (data.status === "success") {
        addRuleToTable(veTrai, vePhai, data.index);
        hideModal();
      } else {
        alert("Lỗi khi thêm luật: " + data.message);
      }
    } catch (error) {
      console.error("Error adding rule:", error);
      alert("Lỗi kết nối khi thêm luật.");
    }
  }
}

const helpModal = document.getElementById("helpModal");
const helpModalTitle = document.getElementById("helpModalTitle");
const helpModalBody = document.getElementById("helpModalBody");

const fpgHelpContent = `
  <h3>Giải thích Đồ thị FPG (Facts Precedence Graph)</h3>
  <p>
    Đồ thị FPG biểu diễn mối quan hệ
    <b>tiền đề -> kết luận</b> giữa các <b>sự kiện (facts)</b>.
  </p>
  <ul>
    <li>
      Mỗi <b>nút (node)</b> là một sự kiện (ví dụ: 'a', 'b').
    </li>
    <li>
      Một <b>cung (edge)</b> đi từ 'a' đến 'b' có nghĩa
      là "sự kiện 'a' là tiền đề để suy ra sự kiện 'b' thông qua
      một (hoặc nhiều) luật".
    </li>
    <li>
      Các nút <b>Giả thiết (GT)</b> (nếu có) được tô màu xanh.
    </li>
    <li>
      Các nút <b>Kết luận (KL)</b> (nếu có) được tô màu đỏ.
    </li>
  </ul>
`;

const rpgHelpContent = `
  <h3>Giải thích Đồ thị RPG (Rules Precedence Graph)</h3>
  <p>
    Đồ thị RPG biểu diễn mối quan hệ <b>trước-sau</b> giữa các <b>luật (rules)</b>.
  </p>
  <ul>
    <li>Mỗi <b>nút (node)</b> là một luật (ví dụ: 'r1', 'r2').</li>
    <li>
      Một <b>cung (edge)</b> đi từ 'r1' đến 'r2' có nghĩa là "luật r1
      sinh ra một sự kiện, và sự kiện đó là tiền đề của luật r2". (r1
      liên hệ trước r2).
    </li>
    <li>
      Các nút <b>RGT</b> (luật có thể được kích hoạt ngay bởi GT)
      được tô màu xanh.
    </li>
    <li>
      Các nút <b>RKL</b> (luật sinh ra kết luận KL) được tô màu đỏ.
    </li>
  </ul>
`;

function showHelpModal(type) {
  if (type === "fpg") {
    helpModalTitle.textContent = "Hướng dẫn đọc đồ thị FPG";
    helpModalBody.innerHTML = fpgHelpContent;
  } else if (type === "rpg") {
    helpModalTitle.textContent = "Hướng dẫn đọc đồ thị RPG";
    helpModalBody.innerHTML = rpgHelpContent;
  }
  helpModal.style.display = "flex";
}

function hideHelpModal() {
  helpModal.style.display = "none";
}

// --- CÁC HÀM XỬ LÝ BẢNG (TABLE) ---
const tableBody = document
  .getElementById("ruleTable")
  .getElementsByTagName("tbody")[0];

async function loadRulesFromAPI() {
  try {
    const response = await fetch(`${API_URL}/api/rules`);
    const rules = await response.json();
    tableBody.innerHTML = ""; // Xóa bảng cũ
    rules.forEach((rule) => {
      addRuleToTable(rule.left, rule.right, rule.index);
    });
  } catch (error) {
    console.error("Error loading rules:", error);
    alert("Không thể tải danh sách luật từ server.");
  }
}

function addRuleToTable(veTrai, vePhai, ruleIndex) {
  const newRow = tableBody.insertRow();
  newRow.setAttribute("data-index", ruleIndex);
  newRow.insertCell(0).textContent = veTrai;
  newRow.insertCell(1).textContent = vePhai;
  const actionCell = newRow.insertCell(2);
  actionCell.className = "action-cell";
  actionCell.innerHTML = `
                <button class="btn-edit" onclick="editRule(${ruleIndex})">Sửa</button>
                <button class.btn-delete" onclick="deleteRule(${ruleIndex}, this)">Xóa</button>
            `;
}

function updateRuleInTable(ruleIndex, veTrai, vePhai) {
  const row = tableBody.querySelector(`tr[data-index="${ruleIndex}"]`);
  if (row) {
    row.cells[0].textContent = veTrai;
    row.cells[1].textContent = vePhai;
  }
}

function editRule(ruleIndex) {
  showModal("edit", ruleIndex);
}

async function deleteRule(ruleIndex, button) {
  if (confirm("Bạn có chắc chắn muốn xóa luật này không?")) {
    try {
      const response = await fetch(`${API_URL}/api/rules/${ruleIndex}`, {
        method: "DELETE",
      });
      const data = await response.json();
      if (data.status === "success") {
        loadRulesFromAPI(); // Tải lại bảng để đồng bộ index
      } else {
        alert("Lỗi khi xóa luật: " + data.message);
      }
    } catch (error) {
      console.error("Error deleting rule:", error);
      alert("Lỗi kết nối khi xóa luật.");
    }
  }
}

async function deleteAllRules() {
  if (
    confirm(
      "BẠN CÓ CHẮC CHẮN MUỐN XÓA TOÀN BỘ LUẬT KHÔNG?\n\nHành động này không thể hoàn tác."
    )
  ) {
    try {
      const response = await fetch(`${API_URL}/api/rules/clear_all`, {
        method: "DELETE",
      });
      const data = await response.json();
      if (data.status === "success") {
        loadRulesFromAPI();
        alert("Đã xóa tất cả luật thành công.");
      } else {
        alert("Lỗi khi xóa tất cả luật: " + data.message);
      }
    } catch (error) {
      console.error("Error clearing all rules:", error);
      alert("Lỗi kết nối khi xóa tất cả luật.");
    }
  }
}

// --- 5. HÀM VẼ ĐỒ THỊ ---

function drawGraph(containerId, graphData, direction = "LR") {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  const data = {
    nodes: new vis.DataSet(graphData.nodes),
    edges: new vis.DataSet(graphData.edges),
  };

  const options = {
    layout: {
      hierarchical: {
        direction: direction,
        sortMethod: "directed",
        levelSeparation: 200,
        nodeSpacing: 250,
      },
    },
    edges: {
      arrows: "to",
      font: { align: "top" },
      smooth: true,
    },
    nodes: {
      shape: "ellipse",
      margin: 10,
    },
    groups: {
      gt: {
        color: { background: "#D4E6F1", border: "#2E86C1" },
        font: { color: "#2E86C1" },
      },
      kl: {
        color: { background: "#FADBD8", border: "#C0392B" },
        font: { color: "#C0392B" },
      },
      proven: {
        color: { background: "#D5F5E3", border: "#28B463" },
      },
      failed: {
        color: { background: "#FADBD8", border: "#C0392B" },
      },
      loop: {
        color: { background: "#FDEBD0", border: "#F39C12" },
      },
    },
    interaction: {
      dragNodes: false,
      dragView: true,
      hover: true,
    },
    physics: {
      enabled: true,
      solver: "hierarchicalRepulsion",
    },
  };

  const network = new vis.Network(container, data, options);
  network.fit();
}

function getFactsAndGoalsForGraph() {
  const gtForward = document.getElementById("facts-input-forward").value;
  const klForward = document.getElementById("goal-input-forward").value;
  const gtBackward = document.getElementById("facts-input-backward").value;
  const klBackward = document.getElementById("goal-input-backward").value;

  const gt = (gtForward || gtBackward || "")
    .split(",")
    .map((f) => f.trim())
    .filter((f) => f);
  const kl = (klForward || klBackward || "")
    .split(",")
    .map((f) => f.trim())
    .filter((f) => f);

  return { gt: gt.join(","), kl: kl.join(",") };
}

async function drawFPG() {
  const { gt, kl } = getFactsAndGoalsForGraph();
  try {
    const response = await fetch(`${API_URL}/api/fpg`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gt, kl }),
    });
    const graphData = await response.json();
    drawGraph("fpg-canvas", graphData, "LR");
  } catch (e) {
    const errorMsg = "Lỗi khi vẽ đồ thị FPG. " + e.message;
    document.getElementById("fpg-canvas").innerText = errorMsg;
    console.error("Lỗi FPG:", e);
  }
}

async function drawRPG() {
  const { gt, kl } = getFactsAndGoalsForGraph();
  try {
    const response = await fetch(`${API_URL}/api/rpg`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gt, kl }),
    });
    const graphData = await response.json();
    drawGraph("rpg-canvas", graphData, "LR");
  } catch (e) {
    const errorMsg = "Lỗi khi vẽ đồ thị RPG. " + e.message;
    document.getElementById("rpg-canvas").innerText = errorMsg;
    console.error("Lỗi RPG:", e);
  }
}

// --- 6. HÀM SUY DIỄN ---

function writeLog(logElementId, logArray) {
  const logEl = document.getElementById(logElementId);
  logEl.innerHTML = "";
  logArray.forEach((line) => {
    const p = document.createElement("p");
    p.textContent = line;
    logEl.appendChild(p);
  });
}

function drawTraceTable(containerId, traceData) {
  const container = document.getElementById(containerId);
  if (!traceData || traceData.length === 0) {
    container.innerHTML = "(Không có dữ liệu bảng tóm tắt.)";
    return;
  }

  const table = document.createElement("table");
  table.className = "content-table";

  table.innerHTML = `
    <thead>
      <tr>
        <th>r (Luật)</th>
        <th>THOA</th>
        <th>TG</th>
        <th>R (Luật còn lại)</th>
        <th>VET</th>
      </tr>
    </thead>
  `;

  const tbody = document.createElement("tbody");
  traceData.forEach((step) => {
    const row = tbody.insertRow();
    row.insertCell(0).textContent = step.r;
    row.insertCell(1).textContent = step.thoa;
    row.insertCell(2).textContent = step.tg;
    row.insertCell(3).textContent = step.r_remaining;
    row.insertCell(4).textContent = step.vet;
  });
  table.appendChild(tbody);

  container.innerHTML = "";
  container.appendChild(table);
}

async function runForwardChaining(event) {
  event.preventDefault();
  const logWrapper = document.getElementById("log-forward");
  const tableEl = document.getElementById("table-forward-container");

  logWrapper.innerHTML = "(Đang suy diễn...)";
  tableEl.innerHTML = "";
  logWrapper.parentElement.classList.remove("split-left");

  const facts = document.getElementById("facts-input-forward").value;
  const goal = document.getElementById("goal-input-forward").value;
  const method = document.querySelector('input[name="forward-method"]:checked').value;

  try {
    const response = await fetch(`${API_URL}/api/forward`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ facts, goal, method }),
    });
    const data = await response.json();

    // 1. TẠO BUTTON HƯỚNG DẪN
    const guideBtn = createGuideButton('forward', method);

    // 2. XỬ LÝ HIỂN THỊ LOG
    if (method === 'fpg' || method === 'rpg') {
         logWrapper.innerHTML = `
            <div class="split-container">
                <div class="split-left" id="forward-split-log"></div>
                <div class="split-right" id="forward-split-graph"></div>
            </div>
         `;
         
         const splitLog = document.getElementById("forward-split-log");
         
         // CHÈN BUTTON VÀO ĐẦU LOG
         splitLog.appendChild(guideBtn); 
         
         // CHÈN LOG TEXT
         data.log.forEach((line) => {
            const div = document.createElement("div");
            div.innerHTML = line;
            div.style.marginBottom = "10px";
            splitLog.appendChild(div);
         });
         
         if (data.graph_data) {
             drawGraph("forward-split-graph", data.graph_data, "LR");
         } else {
             document.getElementById("forward-split-graph").innerText = "(Không có dữ liệu đồ thị)";
         }

    } else {
        // LAYOUT THƯỜNG
        logWrapper.innerHTML = "";
        
        // CHÈN BUTTON VÀO ĐẦU LOG
        logWrapper.appendChild(guideBtn);

        data.log.forEach((line) => {
            const div = document.createElement("div");
            div.innerHTML = line;
            div.style.marginBottom = "10px";
            logWrapper.appendChild(div);
        });
    }

    drawTraceTable("table-forward-container", data.trace_table);
    
  } catch (e) {
    logWrapper.innerHTML = "Lỗi: " + e.message;
  }
}
// 🚩 HÀM MỚI: Đệ quy vẽ cây log từ đối tượng JSON
// --- Cập nhật hàm buildLogTree để hiển thị calc_log ---
function buildLogTree(logNode) {
    const li = document.createElement("li");
    li.className = "log-tree-node status-" + logNode.status;
  
    const span = document.createElement("span");
    span.textContent = logNode.text;
    
    span.onclick = (e) => {
      e.stopPropagation();
      li.classList.toggle("collapsed");
    };
    li.appendChild(span);
  
    // [NEW] Hiển thị log tính toán FPG nếu có
    if (logNode.calc_log) {
        const calcDiv = document.createElement("div");
        calcDiv.innerHTML = logNode.calc_log; // Sử dụng innerHTML vì backend trả về thẻ <br>, <b>
        li.appendChild(calcDiv);
    }
  
    if (logNode.children && logNode.children.length > 0) {
      const ul = document.createElement("ul");
      ul.className = "log-tree-children";
      if (logNode.status === 'failed') {
          li.classList.add('collapsed');
      }
      logNode.children.forEach((childNode) => {
        ul.appendChild(buildLogTree(childNode));
      });
      li.appendChild(ul);
    }
  
    return li;
}

// --- Cập nhật hàm runBackwardChaining ---
async function runBackwardChaining(event) {
    event.preventDefault();
    
    const logContainer = document.getElementById("log-backward");
    const facts = document.getElementById("facts-input-backward").value;
    const goal = document.getElementById("goal-input-backward").value;
    const method = document.querySelector('input[name="backward-option"]:checked').value;
  
    logContainer.innerHTML = "(Đang tìm kiếm...)";
    logContainer.parentElement.classList.remove("split-left");
  
    try {
      const response = await fetch(`${API_URL}/api/backward`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ facts, goal, method }),
      });
      const data = await response.json();
      
      // 1. TẠO BUTTON HƯỚNG DẪN
      // Chúng ta sẽ chèn button này vào chuỗi HTML hoặc appendChild sau
      const guideBtn = createGuideButton('backward', method);
      
      let logContentHTML = "";
      if (data.summary_log) {
          data.summary_log.forEach(line => logContentHTML += `<p>${line}</p>`);
          logContentHTML += "<hr>";
      }
      if (data.linear_log) {
          data.linear_log.forEach(stepHtml => logContentHTML += stepHtml);
      }
      
      if (method === 'fpg') {
          logContainer.innerHTML = `
            <div class="split-container">
                <div class="split-left" id="split-log-content"></div>
                <div class="split-right" id="split-fpg-canvas"></div>
            </div>
          `;
          
          const splitLog = document.getElementById("split-log-content");
          // CHÈN BUTTON TRƯỚC
          splitLog.appendChild(guideBtn);
          // CHÈN NỘI DUNG LOG SAU
          // Lưu ý: phải dùng div wrap hoặc insertAdjacentHTML vì guideBtn là Element object
          const contentDiv = document.createElement('div');
          contentDiv.innerHTML = logContentHTML;
          splitLog.appendChild(contentDiv);
          
          if (data.fpg_data) drawGraph("split-fpg-canvas", data.fpg_data, "LR");
          
      } else {
          logContainer.innerHTML = "";
          logContainer.appendChild(guideBtn);
          const contentDiv = document.createElement('div');
          contentDiv.innerHTML = logContentHTML;
          logContainer.appendChild(contentDiv);
      }
      
      if (data.graph_data) {
          drawGraph("backward-graph-canvas", data.graph_data, "RL");
      }
  
    } catch (e) {
      logContainer.innerHTML = "Lỗi: " + e.message;
    }
}