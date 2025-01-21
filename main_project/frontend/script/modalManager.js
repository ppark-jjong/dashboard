export class ModalManager {
  constructor(controller) {
    this.controller = controller;
    this.elements = {
      // 기존 모달
      detailModal: document.getElementById('detail-modal'),
      driverAssignModal: document.getElementById('driver-assign-modal'),
      detailModalContent: document.getElementById('detail-modal-content'),
      selectedDpsList: document.getElementById('selected-dps-list'),
      selectedDpsCount: document.getElementById('selected-dps-count'),
      driverAssignDropdown: document.getElementById('driver-assign-dropdown'),

      // 생성 모달
      createDashboardModal: document.getElementById('create-dashboard-modal'),
      createDashboardForm: document.getElementById('create-dashboard-form'),
    };

    this.currentItem = null;
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    this.setupDetailModalEvents();
    this.setupDriverAssignModalEvents();
    this.setupCreateModalEvents();
    this.setupKeyboardEvents();
    this.setupOutsideClickEvents();
  }

  setupOutsideClickEvents() {
    const modals = [
      this.elements.detailModal,
      this.elements.driverAssignModal,
      this.elements.createDashboardModal,
    ];

    modals.forEach((modal) => {
      if (modal) {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) {
            this.hideModal(modal);
          }
        });
      }
    });
  }

  setupKeyboardEvents() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModals = [
          this.elements.detailModal,
          this.elements.driverAssignModal,
          this.elements.createDashboardModal,
        ].filter((modal) => modal?.style.display === 'block');

        if (openModals.length > 0) {
          this.hideModal(openModals[openModals.length - 1]);
        }
      }
    });
  }

  setupCreateModalEvents() {
    if (
      !this.elements.createDashboardModal ||
      !this.elements.createDashboardForm
    )
      return;

    // Close 버튼 이벤트
    const closeButtons = this.elements.createDashboardModal.querySelectorAll(
      '.close, .btn-secondary'
    );
    closeButtons.forEach((button) => {
      button.addEventListener('click', () =>
        this.hideModal(this.elements.createDashboardModal)
      );
    });

    // 폼 제출 이벤트
    this.elements.createDashboardForm.addEventListener(
      'submit',
      this.handleDashboardCreate.bind(this)
    );

    // 입력 필드 변경 시 유효성 검사
    this.elements.createDashboardForm.addEventListener(
      'input',
      this.validateCreateForm.bind(this)
    );
  }

  validateCreateForm(form) {
    const dpsValue = form.querySelector('#dps').value;

    // DPS 검증 (10자리 숫자)
    const dpsPattern = /^\d{10}$/;
    if (!dpsPattern.test(dpsValue)) {
      return {
        isValid: false,
        message: 'DPS는 10자리 숫자로 입력해주세요.',
      };
    }

    // ETA 형식 검증
    const etaInput = form.querySelector('#eta');
    if (etaInput.value) {
      const etaDate = new Date(etaInput.value);
      if (isNaN(etaDate.getTime())) {
        return {
          isValid: false,
          message: '올바른 날짜 형식을 입력해주세요.',
        };
      }
    }

    // 모든 필수 필드 검증
    const emptyFields = Array.from(form.querySelectorAll('[required]')).filter(
      (input) => !input.value.trim()
    );
    if (emptyFields.length > 0) {
      return {
        isValid: false,
        message: '모든 필드를 입력해주세요.',
      };
    }

    return { isValid: true };
  }

  async handleDashboardCreate(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');

    try {
      submitButton.disabled = true;
      const formData = new FormData(form);
      const dashboardData = {
        type: formData.get('type'),
        status: '대기',
        department: formData.get('department'),
        postal_code: formData.get('postal_code'),
        region: formData.get('region'),
        address: formData.get('address'),
        customer: formData.get('customer'),
        contact: formData.get('contact'),
        warehouse: formData.get('warehouse'),
        remark: formData.get('remark'),
        sla: formData.get('sla'),
        eta: formData.get('eta')
          ? new Date(formData.get('eta')).toISOString()
          : null,
        duration_time: formData.get('duration_time')
          ? parseInt(formData.get('duration_time'))
          : null,
      };

      await this.controller.createDashboard(dashboardData);
      this.hideModal(this.elements.createDashboardModal);
      form.reset();
    } catch (error) {
      const errorMessage = document.getElementById('create-error-message');
      if (errorMessage) {
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
      }
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
      }
    }
  }

  showCreateModal() {
    if (!this.elements.createDashboardModal) return;

    // 폼 초기화
    this.elements.createDashboardForm?.reset();
    const errorMessage = document.getElementById('create-error-message');
    if (errorMessage) {
      errorMessage.style.display = 'none';
    }

    this.showModal(this.elements.createDashboardModal);
  }

  showModal(modal) {
    if (!modal) return;

    // 다른 모달들 숨기기
    [
      this.elements.detailModal,
      this.elements.driverAssignModal,
      this.elements.createDashboardModal,
    ].forEach((m) => {
      if (m && m !== modal) {
        this.hideModal(m);
      }
    });

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    // 첫 번째 입력 필드에 포커스
    const firstInput = modal.querySelector(
      'input:not([type="hidden"]), select, textarea'
    );
    if (firstInput) {
      firstInput.focus();
    }
  }

  hideModal(modal) {
    if (!modal) return;
    modal.style.display = 'none';

    // 다른 모달이 열려있지 않은 경우에만 스크롤 복원
    const otherModalsOpen = [
      this.elements.detailModal,
      this.elements.driverAssignModal,
      this.elements.createDashboardModal,
    ].some((m) => m && m !== modal && m.style.display === 'block');

    if (!otherModalsOpen) {
      document.body.style.overflow = '';
    }
  }

  // 기존 메서드들...
  setupDetailModalEvents() {
    if (!this.elements.detailModal) return;

    const closeButtons = this.elements.detailModal.querySelectorAll(
      '.close, .btn-secondary'
    );
    closeButtons.forEach((button) => {
      button.addEventListener('click', () =>
        this.hideModal(this.elements.detailModal)
      );
    });

    const saveButton = this.elements.detailModal.querySelector('#save-status');
    if (saveButton) {
      saveButton.addEventListener('click', this.handleStatusSave.bind(this));
    }
  }

  setupDriverAssignModalEvents() {
    if (!this.elements.driverAssignModal) return;

    const closeButtons = this.elements.driverAssignModal.querySelectorAll(
      '.close, #cancel-driver-assign'
    );
    closeButtons.forEach((button) => {
      button.addEventListener('click', () =>
        this.hideModal(this.elements.driverAssignModal)
      );
    });

    const confirmButton = this.elements.driverAssignModal.querySelector(
      '#confirm-driver-assign'
    );
    if (confirmButton) {
      confirmButton.addEventListener(
        'click',
        this.handleDriverAssign.bind(this)
      );
    }
  }

  async handleStatusSave() {
    const selectedStatus = this.elements.detailModal.querySelector(
      'input[name="status"]:checked'
    )?.value;

    if (
      selectedStatus &&
      this.currentItem &&
      this.currentItem.status !== selectedStatus
    ) {
      const success = await this.controller.updateStatus(
        this.currentItem.dps,
        selectedStatus
      );
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

    const success = await this.controller.assignDriver(
      selectedDriverId,
      this.selectedDpsList
    );
    if (success) {
      this.hideModal(this.elements.driverAssignModal);
    }
  }

  getDetailModalContent(item) {
    const location = `${item.city || item.region || ''} ${
      item.district || ''
    }`.trim();
    return `
      <div class="modal-header">
        <div class="modal-title">
          <i class="fas fa-box"></i> ${item.dps || '-'}
        </div>
        <div class="modal-subtitle">
          ${item.type || '-'} · ${item.department || '-'}
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
                ${location} ${item.address || ''}
              </span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">우편번호</span>
              <span class="info-value">${item.postal_code || '-'}</span>
            </div>
            <div class="info-item">
              <span class="info-label">SLA</span>
              <span class="info-value">${item.sla || '-'}</span>
            </div>
            <div class="info-item">
              <span class="info-label">창고</span>
              <span class="info-value">${item.warehouse || '-'}</span>
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
              <span class="info-value">${item.duration_time || '-'}분</span>
            </div>
            <div class="info-item">
              <span class="info-label">ETA</span>
              <span class="info-value">${this.controller.view.formatDate(
                item.eta
              )}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">출발 시간</span>
              <span class="info-value">${this.controller.view.formatDate(
                item.depart_time
              )}</span>
            </div>
            <div class="info-item">
              <span class="info-label">완료 시간</span>
              <span class="info-value">${this.controller.view.formatDate(
                item.completed_time
              )}</span>
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
              <span class="info-value">${item.driver_name || '-'}</span>
            </div>
            <div class="info-item">
              <span class="info-label">기사 연락처</span>
              <span class="info-value">${item.driver_contact || '-'}</span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-item">
              <span class="info-label">고객명</span>
              <span class="info-value">${item.customer || '-'}</span>
            </div>
            <div class="info-item">
              <span class="info-label">고객 연락처</span>
              <span class="info-value">${item.contact || '-'}</span>
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
        </div>
      `
          : ''
      }

      <div class="status-select-container">
        <h4><i class="fas fa-exchange-alt"></i>상태 변경</h4>
        <div class="status-select-grid">
          ${['대기', '진행', '완료', '이슈']
            .map(
              (status) => `
              <div class="status-option">
                <input type="radio" id="status-${status}" name="status" value="${status}"
                  ${item.status === status ? 'checked' : ''}>
                <label for="status-${status}">
                  <i class="fas ${
                    status === '대기'
                      ? 'fa-hourglass-start'
                      : status === '진행'
                      ? 'fa-spinner'
                      : status === '완료'
                      ? 'fa-check-circle'
                      : 'fa-exclamation-circle'
                  } status-icon"></i>
                  <span class="status-text">${status}</span>
                </label>
              </div>
            `
            )
            .join('')}
        </div>
      </div>
    `;
  }
}
