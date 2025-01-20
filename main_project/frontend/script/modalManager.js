export class ModalManager {
  constructor(controller) {
    this.controller = controller;
    this.elements = {
      detailModal: document.getElementById("detail-modal"),
      driverAssignModal: document.getElementById("driver-assign-modal"),
      detailModalContent: document.getElementById("detail-modal-content"),
      selectedDpsList: document.getElementById("selected-dps-list"),
      selectedDpsCount: document.getElementById("selected-dps-count"),
      driverAssignDropdown: document.getElementById("driver-assign-dropdown")
    };

    this.initializeEventListeners();
  }

  initializeEventListeners() {
    this.setupDetailModalEvents();
    this.setupDriverAssignModalEvents();
    this.setupKeyboardEvents();
  }

  setupKeyboardEvents() {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (this.elements.detailModal?.style.display === "block") {
          this.hideModal(this.elements.detailModal);
        }
        if (this.elements.driverAssignModal?.style.display === "block") {
          this.hideModal(this.elements.driverAssignModal);
        }
      }
    });
  }

  setupDetailModalEvents() {
    if (!this.elements.detailModal) return;

    // 닫기 버튼 이벤트
    const closeButtons = this.elements.detailModal.querySelectorAll(".close, .btn-secondary");
    closeButtons.forEach(button => {
      button.addEventListener("click", () => this.hideModal(this.elements.detailModal));
    });

    // 모달 외부 클릭 시 닫기
    this.elements.detailModal.addEventListener("click", (e) => {
      if (e.target === this.elements.detailModal) {
        this.hideModal(this.elements.detailModal);
      }
    });

    // 상태 저장 버튼 이벤트
    const saveButton = this.elements.detailModal.querySelector("#save-status");
    if (saveButton) {
      saveButton.addEventListener("click", this.handleStatusSave.bind(this));
    }
  }

  setupDriverAssignModalEvents() {
    if (!this.elements.driverAssignModal) return;

    // 닫기 버튼 이벤트
    const closeButtons = this.elements.driverAssignModal.querySelectorAll(".close, #cancel-driver-assign");
    closeButtons.forEach(button => {
      button.addEventListener("click", () => this.hideModal(this.elements.driverAssignModal));
    });

    // 모달 외부 클릭 시 닫기
    this.elements.driverAssignModal.addEventListener("click", (e) => {
      if (e.target === this.elements.driverAssignModal) {
        this.hideModal(this.elements.driverAssignModal);
      }
    });

    // 할당 버튼 이벤트
    const confirmButton = this.elements.driverAssignModal.querySelector("#confirm-driver-assign");
    if (confirmButton) {
      confirmButton.addEventListener("click", this.handleDriverAssign.bind(this));
    }
  }

  hideModal(modal) {
    if (modal) {
      modal.style.display = "none";
      document.body.style.overflow = "";
    }
  }

  showModal(modal) {
    if (modal) {
      modal.style.display = "block";
      document.body.style.overflow = "hidden";
    }
  }

  async showDetailModal(item) {
    if (!this.elements.detailModal || !this.elements.detailModalContent) return;

    this.currentItem = item;
    this.elements.detailModalContent.innerHTML = this.getDetailModalContent(item);
    this.showModal(this.elements.detailModal);
  }

  showDriverAssignModal(selectedDps) {
    if (!this.elements.driverAssignModal || !selectedDps.length) return;

    // 선택된 DPS 목록 표시
    if (this.elements.selectedDpsList) {
      this.elements.selectedDpsList.innerHTML = selectedDps
        .map(dps => `<div class="dps-item">${dps}</div>`)
        .join('');
    }

    // 선택된 DPS 개수 표시
    if (this.elements.selectedDpsCount) {
      this.elements.selectedDpsCount.textContent = selectedDps.length;
    }

    this.showModal(this.elements.driverAssignModal);
    this.selectedDpsList = selectedDps;
  }

  async handleStatusSave() {
    const selectedStatus = this.elements.detailModal.querySelector('input[name="status"]:checked')?.value;

    if (selectedStatus && this.currentItem && this.currentItem.status !== selectedStatus) {
      const success = await this.controller.updateStatus(this.currentItem.dps, selectedStatus);
      if (success) {
        this.hideModal(this.elements.detailModal);
      }
    }
  }

  async handleDriverAssign() {
    const selectedDriverId = this.elements.driverAssignDropdown?.value;

    if (!selectedDriverId) {
      this.controller.view.showToast('알림', '기사를 선택해주세요.');
      return;
    }

    const success = await this.controller.assignDriver(selectedDriverId, this.selectedDpsList);
    if (success) {
      this.hideModal(this.elements.driverAssignModal);
    }
  }

  getDetailModalContent(item) {
    const location = `${item.city || item.region || ''} ${item.district || ''}`.trim();
    return `
      <div class="modal-header">
        <div class="modal-title">
          <i class="fas fa-box"></i> ${item.dps || "-"}
        </div>
        <div class="modal-subtitle">
          ${item.type || "-"} · ${item.department || "-"}
          <span class="status-pill status-${item.status}">${item.status}</span>
        </div>
      </div>

      <!-- 배송 정보 -->
      <div class="info-section">
        <h4><i class="fas fa-map-marker-alt"></i>배송 정보</h4>
        <div class="info-grid">
          <div class="info-row address-row">
            <div class="info-item full-width">
              <span class="info-label">배송지</span>
              <span class="info-value address">
                ${location} ${item.address || ""}
              </span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">우편번호</span>
              <span class="info-value">${item.postal_code || "-"}</span>
            </div>
            <div class="info-item">
              <span class="info-label">SLA</span>
              <span class="info-value">${item.sla || "-"}</span>
            </div>
            <div class="info-item">
              <span class="info-label">창고</span>
              <span class="info-value">${item.warehouse || "-"}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 시간 정보 -->
      <div class="info-section">
        <h4><i class="fas fa-clock"></i>시간 정보</h4>
        <div class="info-grid">
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">예상 소요시간</span>
              <span class="info-value">${item.duration_time || "-"}분</span>
            </div>
            <div class="info-item">
              <span class="info-label">ETA</span>
              <span class="info-value">${this.controller.view.formatDate(item.eta)}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">출발 시간</span>
              <span class="info-value">${this.controller.view.formatDate(item.depart_time)}</span>
            </div>
            <div class="info-item">
              <span class="info-label">완료 시간</span>
              <span class="info-value">${this.controller.view.formatDate(item.completed_time)}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 담당자 정보 -->
      <div class="info-section">
        <h4><i class="fas fa-user"></i>담당자 정보</h4>
        <div class="info-grid">
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">기사명</span>
              <span class="info-value">${item.driver_name || "-"}</span>
            </div>
            <div class="info-item">
              <span class="info-label">기사 연락처</span>
              <span class="info-value">${item.driver_contact || "-"}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">고객명</span>
              <span class="info-value">${item.customer || "-"}</span>
            </div>
            <div class="info-item">
              <span class="info-label">고객 연락처</span>
              <span class="info-value">${item.contact || "-"}</span>
            </div>
          </div>
        </div>
      </div>

      ${item.remark ? `
        <div class="info-section">
          <h4><i class="fas fa-sticky-note"></i>특이사항</h4>
          <div class="info-grid">
            <div class="info-item full-width">
              <span class="info-value remark">${item.remark}</span>
            </div>
          </div>
        </div>
      ` : ''}

      <div class="status-select-container">
        <h4><i class="fas fa-exchange-alt"></i>상태 변경</h4>
        <div class="status-select-grid">
          ${["대기", "진행", "완료", "이슈"]
        .map((status) => `
              <div class="status-option">
                <input type="radio" id="status-${status}" name="status" value="${status}"
                  ${item.status === status ? "checked" : ""}>
                <label for="status-${status}">
                  <i class="fas ${status === "대기"
            ? "fa-hourglass-start"
            : status === "진행"
              ? "fa-spinner"
              : status === "완료"
                ? "fa-check-circle"
                : "fa-exclamation-circle"
          } status-icon"></i>
                  <span class="status-text">${status}</span>
                </label>
              </div>
            `)
        .join("")}
        </div>
      </div>
    `;
  }
}