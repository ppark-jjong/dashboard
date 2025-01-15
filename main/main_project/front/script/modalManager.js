class ModalManager {
  constructor(app) {
    this.app = app;
    this.detailModal = document.getElementById("detail-modal");
    this.driverAssignModal = document.getElementById("driver-assign-modal");
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    this.setupDetailModalEvents();
    this.setupDriverAssignModalEvents();
  }

  setupDetailModalEvents() {
    if (!this.detailModal) return;

    const closeButton = this.detailModal.querySelector(".close");
    if (closeButton) {
      closeButton.addEventListener("click", () =>
        this.hideModal(this.detailModal)
      );
    }

    this.detailModal.addEventListener("click", (e) => {
      if (e.target === this.detailModal) this.hideModal(this.detailModal);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.detailModal.style.display === "block") {
        this.hideModal(this.detailModal);
      }
    });
  }

  setupDriverAssignModalEvents() {
    if (!this.driverAssignModal) return;

    const closeButton = this.driverAssignModal.querySelector(".close");
    if (closeButton) {
      closeButton.addEventListener("click", () =>
        this.hideModal(this.driverAssignModal)
      );
    }

    this.driverAssignModal.addEventListener("click", (e) => {
      if (e.target === this.driverAssignModal) {
        this.hideModal(this.driverAssignModal);
      }
    });

    const cancelButton = this.driverAssignModal.querySelector(
      "#cancel-driver-assign"
    );
    if (cancelButton) {
      cancelButton.addEventListener("click", () =>
        this.hideModal(this.driverAssignModal)
      );
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

  // 상세 모달: item 정보를 채워서 표시
  showDetailModal(item) {
    if (!this.detailModal) return;

    const content = this.detailModal.querySelector("#detail-modal-content");
    if (!content) return;

    content.innerHTML = `
      <div class="modal-header">
        <div class="modal-title">
          <i class="fas fa-box"></i> ${item.dps || "-"}
        </div>
        <div class="modal-subtitle">
          ${item.type || "-"} · ${item.department || "-"}
          <span class="status-pill status-${item.status}">${item.status}</span>
        </div>
      </div>

      <div class="info-section">
        <h4><i class="fas fa-map-marker-alt"></i>배송 정보</h4>
        <div class="info-grid">
          <div class="info-row address-row">
            <div class="info-item full-width">
              <span class="info-label">배송지</span>
              <span class="info-value address">
                ${(item.city || item.region) || ""} ${item.district || ""} ${item.address || ""}
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
              <span class="info-value">${item.eta || "-"}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">출발 시간</span>
              <span class="info-value">${item.depart_time || "-"}</span>
            </div>
            <div class="info-item">
              <span class="info-label">완료 시간</span>
              <span class="info-value">${item.completed_time || "-"}</span>
            </div>
          </div>
        </div>
      </div>

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

      ${
        item.remark
          ? `
        <div class="info-section">
          <h4><i class="fas fa-sticky-note"></i>특이사항</h4>
          <div class="info-grid">
            <div class="info-item full-width">
              <span class="info-value remark">${item.remark}</span>
            </div>
          </div>
        </div>`
          : ""
      }

      <div class="status-select-container">
        <h4><i class="fas fa-exchange-alt"></i>상태 변경</h4>
        <div class="status-select-grid">
          ${["대기", "진행", "완료", "이슈"]
            .map((status) => `
              <div class="status-option">
                <input type="radio" id="status-${status}" name="status" value="${status}"
                  ${item.status === status ? "checked" : ""}>
                <label for="status-${status}">
                  <i class="fas ${
                    status === "대기"
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

    // 버튼 리스너 설정
    this.addDetailModalButtonListeners(item);
    this.showModal(this.detailModal);
  }

  // 상세 모달의 "저장" 버튼 클릭 시 상태 변경 처리
  addDetailModalButtonListeners(item) {
    const saveButton = this.detailModal.querySelector("#save-status");
    if (saveButton) {
      saveButton.addEventListener("click", async () => {
        const selectedStatus = this.detailModal.querySelector(
          'input[name="status"]:checked'
        )?.value;

        if (selectedStatus && item.status !== selectedStatus) {
          try {
            // dashboardApp.js 쪽에 updateItemStatus가 있다고 가정
            const updatedItem = await this.app.updateItemStatus(item, selectedStatus);
            // 업데이트 성공 → 모달 닫고, 데이터 리프레시
            this.app.showToast("성공", "상태가 변경되었습니다.");
            this.hideModal(this.detailModal);
            this.app.refreshData();
          } catch (err) {
            console.error(err);
            this.app.showToast("실패", "상태 변경 중 오류가 발생했습니다.");
          }
        }
      });
    }
  }

  // 기사 할당 모달 표시
  showDriverAssignModal(selectedDps) {
    console.log("Selected DPS for assignment:", selectedDps);

    if (!this.driverAssignModal) {
      console.error("Driver assign modal not found");
      return;
    }

    const selectedDpsList = this.driverAssignModal.querySelector("#selected-dps-list");
    const driverDropdown = this.driverAssignModal.querySelector("#driver-assign-dropdown");
    const selectedDpsCountSpan = this.driverAssignModal.querySelector("#selected-dps-count");

    // 선택된 DPS 목록 표시
    selectedDpsList.innerHTML = "";
    selectedDps.forEach((dps) => {
      const dpsItem = document.createElement("div");
      dpsItem.textContent = dps;
      dpsItem.classList.add("dps-item");
      selectedDpsList.appendChild(dpsItem);
    });

    // 선택된 DPS 수 표시
    selectedDpsCountSpan.textContent = selectedDps.length;

    // 기사 드롭다운 채우기
    driverDropdown.innerHTML = '<option value="">기사를 선택하세요</option>';
    // 기사 목록은 dashboardApp.js에서 updateDriverOptions()가 채울 수도 있으니
    // 여기서 따로 fetch 안 해도 됨. 필요하다면 API 호출해서 채워도 됨.

    this.showModal(this.driverAssignModal);

    // 할당 버튼 이벤트 리스너
    const confirmAssignBtn = this.driverAssignModal.querySelector("#confirm-driver-assign");
    if (confirmAssignBtn) {
      // 기존 이벤트 리스너 제거 (중복 방지)
      confirmAssignBtn.removeEventListener("click", this.handleDriverAssign);

      // 새 이벤트 리스너 추가
      this.handleDriverAssign = async () => {
        const selectedDriverId = driverDropdown.value;

        if (!selectedDriverId) {
          this.app.showToast("알림", "기사를 선택해주세요.");
          return;
        }

        const success = await this.app.assignDriverToDps(selectedDps, selectedDriverId);
        if (success) {
          this.app.showToast("성공", `${selectedDps.length}건 할당 완료`);
          this.hideModal(this.driverAssignModal);
          this.app.selectedRows.clear();
          this.app.updateAssignButton();
          this.app.refreshData();
        } else {
          this.app.showToast("실패", "기사 할당 중 오류가 발생했습니다.");
        }
      };

      confirmAssignBtn.addEventListener("click", this.handleDriverAssign);
    }
  }
}
