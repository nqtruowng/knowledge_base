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
});

// --- HÀM CHO CHỨC NĂNG IMPORT CSV ---
function triggerCsvImport() {
  document.getElementById("csvFileInput").click();
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const content = e.target.result;
    const lines = content.split(/\r?\n/);

    lines.forEach((line) => {
      if (line.trim() === "") return;

      const parts = line.split("->");
      if (parts.length === 2) {
        const veTrai = parts[0].trim();
        const vePhai = parts[1].trim();
        addRuleToTable(veTrai, vePhai);
      }
    });
  };
  reader.readAsText(file);
  event.target.value = null;
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

    const table = document.getElementById("ruleTable");
    const row = table.rows[rowIndex];
    modalVeTrai.value = row.cells[0].textContent;
    modalVePhai.value = row.cells[1].textContent;
  }
  modal.style.display = "flex";
}

function hideModal() {
  modal.style.display = "none";
}

function handleFormSubmit(event) {
  event.preventDefault();
  const veTrai = modalVeTrai.value.trim();
  const vePhai = modalVePhai.value.trim();
  const rowIndex = modalRuleIndex.value;

  if (veTrai === "" || vePhai === "") {
    alert("Vui lòng nhập đầy đủ cả hai vế.");
    return;
  }

  if (rowIndex) {
    updateRuleInTable(rowIndex, veTrai, vePhai);
  } else {
    addRuleToTable(veTrai, vePhai);
  }
  hideModal();
}

// --- CÁC HÀM XỬ LÝ BẢNG (TABLE) ---
const tableBody = document
  .getElementById("ruleTable")
  .getElementsByTagName("tbody")[0];

function addRuleToTable(veTrai, vePhai) {
  const newRow = tableBody.insertRow();

  newRow.insertCell(0).textContent = veTrai;
  newRow.insertCell(1).textContent = vePhai;

  const actionCell = newRow.insertCell(2);
  actionCell.className = "action-cell";
  actionCell.innerHTML = `
                <button class="btn-edit" onclick="editRule(this)">Sửa</button>
                <button class="btn-delete" onclick="deleteRule(this)">Xóa</button>
            `;
}

function updateRuleInTable(rowIndex, veTrai, vePhai) {
  const row = document.getElementById("ruleTable").rows[rowIndex];
  row.cells[0].textContent = veTrai;
  row.cells[1].textContent = vePhai;
}

// --- CÁC HÀM GỌI TỪ NÚT SỬA/XÓA (onclick) ---

function editRule(button) {
  const row = button.closest("tr");
  showModal("edit", row.rowIndex);
}

function deleteRule(button) {
  if (confirm("Bạn có chắc chắn muốn xóa luật này không?")) {
    const row = button.closest("tr");
    row.remove();
  }
}
