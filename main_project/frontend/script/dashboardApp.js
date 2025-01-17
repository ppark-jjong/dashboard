class DashboardApp {
  constructor() {
    this.currentPage = 0;
    this.pageSize = 15;
    this.selectedRows = new Set();

    // 필터에서 department는 제거 또는 주석 처리 (원하면 유지 가능)
    this.filters = {
      // department: "all", // 사용 안 한다면 제거
      status: "all",
      driver: "all",
      search: "",
    };

    this.modalManager = new ModalManager(this);
    this.initializeEventListeners();
    this.setupDriverAssignModal();
    this.refreshData();
  }

  initializeEventListeners() {
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.filters.search = e.target.value;
        this.refreshData();
      });
    }
    document.getElementById("status-filter")?.addEventListener("change", (e) => {
      this.filters.status = e.target.value;
      this.refreshData();
    });

    document.getElementById("driver-select")?.addEventListener("change", (e) => {
      this.filters.driver = e.target.value;
      this.refreshData();
    });

    document.getElementById("refresh-btn")?.addEventListener("click", () => {
      this.refreshData(true);
    });

    document.getElementById("prev-page")?.addEventListener("click", () => {
      if (this.currentPage > 0) {
        this.currentPage--;
        this.refreshData();
      }
    });

    document.getElementById("next-page")?.addEventListener("click", () => {
      const maxPage = Math.ceil(this.filteredData.length / this.pageSize) - 1;
      if (this.currentPage < maxPage) {
        this.currentPage++;
        this.refreshData();
      }
    });

    document.getElementById("select-all")?.addEventListener("change", (e) => {
      const isChecked = e.target.checked;
      const checkboxes = document.querySelectorAll('#table-body input[type="checkbox"]');

      checkboxes.forEach((checkbox) => {
        checkbox.checked = isChecked;
        const rowId = checkbox.getAttribute("data-row-id");
        if (isChecked) {
          this.selectedRows.add(rowId);
        } else {
          this.selectedRows.delete(rowId);
        }
        this.updateRowStyle(checkbox.closest("tr"), isChecked);
      });

      this.updateAssignButton();
    });
  }

  setupDriverAssignModal() {
    const confirmAssignBtn = document.getElementById("confirm-driver-assign");
    const cancelAssignBtn = document.getElementById("cancel-driver-assign");
    const driverDropdown = document.getElementById("driver-assign-dropdown");

    confirmAssignBtn?.addEventListener("click", async () => {
      const selectedDriverId = driverDropdown.value;

      if (!selectedDriverId) {
        this.showToast("알림", "기사를 선택해주세요.");
        return;
      }

      const waitingSelectedDps = this.getWaitingSelectedDps();
      if (waitingSelectedDps.length === 0) {
        this.showToast("알림", "할당 가능한 배송건이 없습니다.");
        return;
      }

      // FastAPI로 기사 할당 API 호출
      const success = await this.assignDriverToDps(waitingSelectedDps, selectedDriverId);

      if (success) {
        this.handleSuccessfulAssignment(selectedDriverId, waitingSelectedDps);
      } else {
        this.showToast("실패", "기사 할당 중 오류가 발생했습니다.");
      }
    });

    cancelAssignBtn?.addEventListener("click", () => {
      this.modalManager.hideModal(document.getElementById("driver-assign-modal"));
    });
  }

  // "대기" 상태인 DPS만 모아서 기사 할당이 가능하다고 가정
  getWaitingSelectedDps() {
    return Array.from(this.selectedRows).filter((dps) => {
      const item = this.filteredData.find((d) => d.dps === dps);
      return item && item.status === "대기";
    });
  }

  // 기사 할당 API (POST)
  async assignDriverToDps(dpsList, driverId) {
    try {
      const res = await fetch("/api/assignDriver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          driver_id: driverId,
          dpsList: dpsList,
        }),
      });
      const json = await res.json();
      return json.success; // true/false
    } catch (err) {
      console.error(err);
      return false;
    }
  }

  handleSuccessfulAssignment(driverId, assignedDps) {
    this.showToast("성공", `${assignedDps.length}건을 기사(${driverId})에게 할당했습니다.`);
    this.modalManager.hideModal(document.getElementById("driver-assign-modal"));

    this.selectedRows.clear();
    this.updateAssignButton();
    this.refreshData();
  }

  // 서버에서 데이터 받아오고, 필터/페이지네이션 적용
  refreshData(showLoading = false) {
    if (showLoading) {
      const loadingOverlay = document.querySelector(".loading-overlay");
      if (loadingOverlay) loadingOverlay.style.display = "flex";
    }

    // status, driver, search, currentPage, pageSize
    const { status, driver, search } = this.filters;
    const page = this.currentPage + 1; // 1-based
    const limit = this.pageSize;

    const params = new URLSearchParams();
    if (status !== "all") params.append("status", status);
    if (driver !== "all") params.append("driver_id", driver);
    // 검색어 처리 (필요하면 서버에 전달) 예) params.append("search", search);
    params.append("page", page);
    params.append("limit", limit);

    fetch(`http://localhost:8000/api/dashboard?${params.toString()}`)
      .then(res => res.json())
      .then(json => {
        // { totalCount, data }를 가정
        const { totalCount, data } = json;

        // 검색어가 있으면 클라이언트 단에서 추가 필터링 할 수도 있음(원하면)
        // 여기선 서버 필터에 맡긴다고 가정
        this.filteredData = data;

        // slice 로직은 서버가 이미 페이지네이션 해줬다고 치면 필요 없음
        // 그렇지 않다면 아래처럼 해도 됨:
        // const start = this.currentPage * this.pageSize;
        // const end = start + this.pageSize;
        // const pageData = data.slice(start, end);

        // 테이블 업데이트
        this.updateTable(data);

        // 페이지네이션
        this.updatePagination(totalCount);

        // 기사 목록 업데이트
        this.updateDriverOptions();

        if (showLoading) {
          const loadingOverlay = document.querySelector(".loading-overlay");
          if (loadingOverlay) loadingOverlay.style.display = "none";
          this.showToast("성공", "데이터가 새로고침되었습니다.");
        }
      })
      .catch(err => {
        console.error(err);
        if (showLoading) {
          const loadingOverlay = document.querySelector(".loading-overlay");
          if (loadingOverlay) loadingOverlay.style.display = "none";
        }
        this.showToast("실패", "데이터 로드 중 오류가 발생했습니다.");
      });
  }

  // 기사 셀렉트 박스 갱신 (필요 시)
  updateDriverOptions() {
    // fetch("/api/drivers") → driver 목록을 받아온다고 가정
    fetch("/api/drivers")
      .then(res => res.json())
      .then(json => {
        const drivers = json.drivers; // 가정: { drivers: [...] }

        const select = document.getElementById("driver-select");
        if (!select) return;

        const currentValue = select.value;
        select.innerHTML = '<option value="all">전체 기사</option>';

        drivers.forEach((driver) => {
          const option = document.createElement("option");
          option.value = driver.id; // driver.id가 문자열인지 숫자인지 확인
          option.textContent = driver.name;
          select.appendChild(option);
        });

        // 기존 선택값 복원
        if (currentValue !== "all") {
          select.value = currentValue;
        }

        // 기사 할당 모달 dropdown도 업데이트
        const assignDropdown = document.getElementById("driver-assign-dropdown");
        if (assignDropdown) {
          assignDropdown.innerHTML = '<option value="">기사를 선택하세요</option>';
          drivers.forEach((driver) => {
            const option = document.createElement("option");
            option.value = driver.id;
            option.textContent = driver.name;
            assignDropdown.appendChild(option);
          });
        }
      })
      .catch(err => console.error("드라이버 목록 로드 오류:", err));
  }

  updateTable(data) {
    const tbody = document.getElementById("table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.forEach((item) => {
      const row = document.createElement("tr");
      const status = item.status && ["대기", "진행", "완료", "이슈"].includes(item.status)
        ? item.status
        : "대기";

      if (status) {
        row.classList.add(`row-${status}`);
      }

      const checkboxCell = document.createElement("td");
      checkboxCell.className = "col-checkbox";
      checkboxCell.innerHTML = `
        <label class="custom-checkbox">
          <input type="checkbox" data-row-id="${item.dps}">
          <span class="checkbox-mark"></span>
        </label>
      `;

      const checkbox = checkboxCell.querySelector('input[type="checkbox"]');
      checkbox.addEventListener("change", (e) => {
        const isChecked = e.target.checked;
        if (isChecked) {
          this.selectedRows.add(item.dps);
        } else {
          this.selectedRows.delete(item.dps);
        }
        this.updateRowStyle(row, isChecked);
        this.updateSelectAllState();
        this.updateAssignButton();
      });

      row.appendChild(checkboxCell);

      const location = `${item.city || item.region || ''} ${item.district || ''}`.trim();
      const columns = [
        { value: item.department || "-", className: "col-department" },
        { value: item.type || "-", className: "col-type" },
        { value: item.warehouse || "-", className: "col-warehouse" },
        { value: item.driver_name || "-", className: "col-driver" },
        { value: item.dps || "-", className: "col-dps" },
        { value: item.sla || "-", className: "col-sla" },
        { value: item.eta || "-", className: "col-eta" },
        {
          value: item.status,
          className: "col-status",
          formatter: (value) => `<span class="status-pill status-${value}">${value}</span>`,
        },
        { value: location || "-", className: "col-location" },
        { value: item.customer || "-", className: "col-customer" },
        { value: item.contact || "-", className: "col-contact" },
      ];

      columns.forEach((col) => {
        const cell = document.createElement("td");
        cell.className = col.className;
        cell.innerHTML = col.formatter ? col.formatter(col.value) : col.value;
        row.appendChild(cell);
      });

      // 행 클릭 시 상세 모달 열기 (체크박스 클릭은 제외)
      row.addEventListener("click", (e) => {
        if (!e.target.closest(".custom-checkbox")) {
          this.modalManager.showDetailModal(item);
        }
      });

      tbody.appendChild(row);
    });

    this.updateSelectAllState();
  }

  updateRowStyle(row, isSelected) {
    ["row-대기", "row-진행", "row-완료", "row-이슈"].forEach((statusClass) => {
      if (row.classList.contains(statusClass)) {
        row.classList.remove(statusClass);
      }
    });

    const statusElement = row.querySelector(".col-status .status-pill");
    if (statusElement) {
      const status = statusElement.textContent.trim();
      if (status && ["대기", "진행", "완료", "이슈"].includes(status)) {
        row.classList.add(`row-${status}`);
      }
    }

    row.classList.toggle("selected", isSelected);
  }

  updateSelectAllState() {
    const selectAllCheckbox = document.getElementById("select-all");
    if (!selectAllCheckbox) return;

    const checkboxes = document.querySelectorAll('#table-body input[type="checkbox"]');
    const checkedCount = document.querySelectorAll('#table-body input[type="checkbox"]:checked').length;

    if (checkboxes.length === 0) {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === 0) {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === checkboxes.length) {
      selectAllCheckbox.checked = true;
      selectAllCheckbox.indeterminate = false;
    } else {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = true;
    }
  }

  updateAssignButton() {
    const assignButton = document.getElementById("assign-btn");
    if (!assignButton) return;

    const waitingSelectedRows = this.getWaitingSelectedDps();
    assignButton.disabled = waitingSelectedRows.length === 0;
    assignButton.classList.toggle("btn-disabled", waitingSelectedRows.length === 0);
  }

  updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / this.pageSize);
    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");
    const pageInfo = document.getElementById("page-info");

    // 이전/다음 버튼 활성화/비활성화 처리
    if (prevBtn) prevBtn.disabled = this.currentPage === 0;
    if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages - 1;
    // 페이지 정보 표시 (예: "1 / 10")
    if (pageInfo) pageInfo.textContent = `${this.currentPage + 1} / ${totalPages}`;
  }

  // 상태 변경 시 사용 (PUT /api/dashboard/:id/status) 등, 필요하면 추가
  async updateItemStatus(item, newStatus) {
    // 예시로 id를 사용. 실제론 dps나 item.id 등 서버 스펙에 맞춰야 함
    const itemId = item.id; 
    try {
      const res = await fetch(`http://localhost:8000/api/dashboard/${itemId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_status: newStatus }),
      });
      const json = await res.json();
      if (json.success) {
        return json.item;
      } else {
        throw new Error("상태 변경 실패");
      }
    } catch (err) {
      console.error(err);
      throw err;
    }
  }

  showToast(header, message) {
    const toast = document.getElementById("notification-toast");
    const toastHeader = toast?.querySelector(".toast-header");
    const toastBody = toast?.querySelector(".toast-body");

    if (!toast || !toastHeader || !toastBody) return;

    toastHeader.textContent = header;
    toastBody.textContent = message;

    toast.style.display = "block";
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        toast.style.display = "none";
      }, 300);
    }, 3000);
  }
}

window.DashboardApp = DashboardApp;

