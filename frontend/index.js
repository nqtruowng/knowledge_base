// Khai báo API endpoint
const API_URL = "http://127.0.0.1:5001"; // Port của server Flask

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
      Một <b>cung (edge)</b> đi từ 'a' đến 'b' (nhãn 'r1') có nghĩa
      là "sự kiện 'a' là tiền đề để suy ra sự kiện 'b' thông qua
      luật r1".
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
                <button class="btn-delete" onclick="deleteRule(${ruleIndex}, this)">Xóa</button>
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
        const row = button.closest("tr");
        row.remove();
      } else {
        alert("Lỗi khi xóa luật: " + data.message);
      }
    } catch (error) {
      console.error("Error deleting rule:", error);
      alert("Lỗi kết nối khi xóa luật.");
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
  const logEl = document.getElementById("log-forward");
  const tableEl = document.getElementById("table-forward-container");

  logEl.innerHTML = "(Đang suy diễn, vui lòng chờ...)";
  tableEl.innerHTML = "";

  const facts = document.getElementById("facts-input-forward").value;
  const goal = document.getElementById("goal-input-forward").value;
  const method = document.querySelector(
    'input[name="forward-method"]:checked'
  ).value;

  try {
    const response = await fetch(`${API_URL}/api/forward`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ facts, goal, method }),
    });
    const data = await response.json();

    writeLog("log-forward", data.log);
    drawTraceTable("table-forward-container", data.trace_table);
  } catch (e) {
    writeLog("log-forward", ["Lỗi kết nối đến server: " + e.message]);
    tableEl.innerHTML = "(Lỗi, không thể tạo bảng)";
  }
}

async function runBackwardChaining(event) {
  event.preventDefault();
  const logEl = document.getElementById("log-backward");
  const graphEl = document.getElementById("backward-graph-canvas");

  logEl.innerHTML = "(Đang tìm kiếm, vui lòng chờ...)";
  graphEl.innerHTML = "(Đồ thị tìm kiếm sẽ xuất hiện ở đây...)";

  const facts = document.getElementById("facts-input-backward").value;
  const goal = document.getElementById("goal-input-backward").value;
  const method = document.querySelector(
    'input[name="backward-option"]:checked'
  ).value;

  try {
    const response = await fetch(`${API_URL}/api/backward`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ facts, goal, method }),
    });
    const data = await response.json();

    writeLog("log-backward", data.log);

    if (data.graph_data) {
      // 🚩 SỬA LỖI: Đổi 'UD' thành 'LR' để vẽ ngang
      drawGraph("backward-graph-canvas", data.graph_data, "LR");
    } else {
      graphEl.innerHTML = "(Không có dữ liệu đồ thị để vẽ)";
    }
  } catch (e) {
    writeLog("log-backward", ["Lỗi kết nối đến server: " + e.message]);
    graphEl.innerHTML = "(Lỗi, không thể vẽ đồ thị)";
  }
}