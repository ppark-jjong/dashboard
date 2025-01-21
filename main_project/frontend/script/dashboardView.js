// dashboardView.js
export class DashboardView {
  constructor() {
    this.elements = {
      // 테이블 관련 요소
      table: document.getElementById('data-table'),
      tableBody: document.getElementById('table-body'),

      // 필터 관련 요소
      searchInput: document.getElementById('search-input'),
      statusFilter: document.getElementById('status-filter'),
      driverSelect: document.getElementById('driver-select'),

      // 버튼 요소
      refreshBtn: document.getElementById('refresh-btn'),
      createBtn: document.getElementById('create-btn'),
      deleteBtn: document.getElementById('delete-btn'),
      assignBtn: document.getElementById('assign-btn'),

      // 체크박스
      selectAll: document.getElementById('select-all'),

      // 페이지네이션
      prevPage: document.getElementById('prev-page'),
      nextPage: document.getElementById('next-page'),
      pageInfo: document.getElementById('page-info'),

      // 기타 UI 요소
      loadingOverlay: document.querySelector('.loading-overlay'),
      toast: document.getElementById('notification-toast'),
    };

    // 초기 상태 설정
    this.state = {
      selectedRows: new Set(),
    };

    this.validateElements();
  }

  validateElements() {
    const missingElements = Object.entries(this.elements)
      .filter(([key, element]) => !element)
      .map(([key]) => key);

    if (missingElements.length > 0) {
      console.error('Missing elements:', missingElements);
    }
  }

  bindEvents(controller) {
    // 필터 이벤트
    this.elements.searchInput?.addEventListener('input', (e) =>
      controller.updateFilter('search', e.target.value)
    );

    this.elements.statusFilter?.addEventListener('change', (e) =>
      controller.updateFilter('status', e.target.value)
    );

    this.elements.driverSelect?.addEventListener('change', (e) =>
      controller.updateFilter('driver', e.target.value)
    );

    // 버튼 이벤트
    this.elements.refreshBtn?.addEventListener('click', () =>
      controller.refreshData(true)
    );

    this.elements.createBtn?.addEventListener('click', () =>
      this.modalManager.showCreateModal()
    );

    this.elements.deleteBtn?.addEventListener('click', () =>
      this.handleDeleteClick(controller)
    );

    // 페이지네이션
    this.elements.prevPage?.addEventListener('click', () =>
      controller.updatePage(controller.state.currentPage - 1)
    );

    this.elements.nextPage?.addEventListener('click', () =>
      controller.updatePage(controller.state.currentPage + 1)
    );

    // 전체 선택
    this.elements.selectAll?.addEventListener('change', (e) => {
      const checkboxes = document.querySelectorAll(
        '#table-body input[type="checkbox"]'
      );
      checkboxes.forEach((checkbox) => {
        checkbox.checked = e.target.checked;
        this.handleRowSelection(
          checkbox.dataset.rowId,
          e.target.checked,
          controller
        );
      });
    });

    // 테이블 행 클릭 이벤트
    this.elements.tableBody?.addEventListener('click', (e) => {
      const row = e.target.closest('tr');
      if (!row) return;

      const checkbox = e.target.closest('input[type="checkbox"]');
      if (checkbox) {
        // 체크박스 클릭
        this.handleRowSelection(
          checkbox.dataset.rowId,
          checkbox.checked,
          controller
        );
      } else {
        // 행 클릭
        const dps = row.querySelector('input[type="checkbox"]')?.dataset.rowId;
        if (dps) {
          this.modalManager.showDetailModal(this.findRowData(dps));
        }
      }
    });
  }

  async handleDeleteClick(controller) {
    if (this.state.selectedRows.size === 0) {
      this.showToast('알림', '삭제할 항목을 선택해주세요.');
      return;
    }

    const confirmMessage = `선택한 ${this.state.selectedRows.size}개 항목을 삭제하시겠습니까?`;
    if (confirm(confirmMessage)) {
      await controller.deleteDashboards(Array.from(this.state.selectedRows));
    }
  }

  handleRowSelection(rowId, isSelected, controller) {
    if (isSelected) {
      this.state.selectedRows.add(rowId);
    } else {
      this.state.selectedRows.delete(rowId);
    }

    this.updateSelectionState();
    controller.updateSelection(rowId, isSelected);
  }

  updateSelectionState() {
    // 삭제 버튼 상태 업데이트
    if (this.elements.deleteBtn) {
      const hasSelection = this.state.selectedRows.size > 0;
      this.elements.deleteBtn.disabled = !hasSelection;
      this.elements.deleteBtn.classList.toggle('btn-disabled', !hasSelection);
    }

    // 할당 버튼 상태 업데이트
    if (this.elements.assignBtn) {
      const hasSelection = this.state.selectedRows.size > 0;
      this.elements.assignBtn.disabled = !hasSelection;
      this.elements.assignBtn.classList.toggle('btn-disabled', !hasSelection);
    }

    // 전체 선택 체크박스 상태 업데이트
    if (this.elements.selectAll) {
      const checkboxes = Array.from(
        document.querySelectorAll('#table-body input[type="checkbox"]')
      );
      const checkedCount = checkboxes.filter((cb) => cb.checked).length;

      if (checkedCount === 0) {
        this.elements.selectAll.checked = false;
        this.elements.selectAll.indeterminate = false;
      } else if (checkedCount === checkboxes.length) {
        this.elements.selectAll.checked = true;
        this.elements.selectAll.indeterminate = false;
      } else {
        this.elements.selectAll.checked = false;
        this.elements.selectAll.indeterminate = true;
      }
    }
  }

  findRowData(dps) {
    const row = this.elements.tableBody
      ?.querySelector(`input[data-row-id="${dps}"]`)
      ?.closest('tr');
    if (!row) return null;

    return {
      dps,
      department: row.querySelector('.col-department').textContent,
      type: row.querySelector('.col-type').textContent,
      warehouse: row.querySelector('.col-warehouse').textContent,
      driver_name: row.querySelector('.col-driver').textContent,
      sla: row.querySelector('.col-sla').textContent,
      eta: row.querySelector('.col-eta').textContent,
      status: row.querySelector('.col-status .status-pill').textContent,
      location: row.querySelector('.col-location').textContent,
      customer: row.querySelector('.col-customer').textContent,
      contact: row.querySelector('.col-contact').textContent,
    };
  }

  renderTable(data) {
    if (!this.elements.tableBody) return;

    this.elements.tableBody.innerHTML = '';
    this.state.selectedRows.clear();
    this.updateSelectionState();

    if (!data.length) {
      this.elements.tableBody.innerHTML = `
                <tr>
                    <td colspan="12" class="text-center">조회된 데이터가 없습니다.</td>
                </tr>`;
      return;
    }

    data.forEach((item) => {
      const row = this.createTableRow(item);
      this.elements.tableBody.appendChild(row);
    });
  }

  createTableRow(item) {
    const row = document.createElement('tr');
    row.dataset.status = item.status;
    row.dataset.dps = item.dps;

    const location = `${item.city || item.region || ''} ${
      item.district || ''
    }`.trim();

    row.innerHTML = `
            <td class="col-checkbox">
                <label class="custom-checkbox">
                    <input type="checkbox" data-row-id="${item.dps}" ${
      this.state.selectedRows.has(item.dps) ? 'checked' : ''
    }>
                    <span class="checkbox-mark"></span>
                </label>
            </td>
            <td class="col-department">${item.department || '-'}</td>
            <td class="col-type">${item.type || '-'}</td>
            <td class="col-warehouse">${item.warehouse || '-'}</td>
            <td class="col-driver">${item.driver_name || '-'}</td>
            <td class="col-dps">${item.dps || '-'}</td>
            <td class="col-sla">${item.sla || '-'}</td>
            <td class="col-eta">${this.formatDate(item.eta)}</td>
            <td class="col-status">
                <span class="status-pill status-${item.status}">${
      item.status
    }</span>
            </td>
            <td class="col-location">${location || '-'}</td>
            <td class="col-customer">${item.customer || '-'}</td>
            <td class="col-contact">${item.contact || '-'}</td>
        `;

    return row;
  }

  formatDate(date) {
    if (!date) return '-';
    return new Intl.DateTimeFormat('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(date));
  }

  updatePagination({ currentPage, totalPages }) {
    if (this.elements.prevPage) {
      this.elements.prevPage.disabled = currentPage === 1;
    }
    if (this.elements.nextPage) {
      this.elements.nextPage.disabled = currentPage >= totalPages;
    }
    if (this.elements.pageInfo) {
      this.elements.pageInfo.textContent = `${currentPage} / ${totalPages}`;
    }
  }

  updateDriverOptions(drivers) {
    if (!this.elements.driverSelect) return;

    const currentValue = this.elements.driverSelect.value;
    this.elements.driverSelect.innerHTML =
      '<option value="all">전체 기사</option>';

    drivers.forEach((driver) => {
      const option = document.createElement('option');
      option.value = driver.driver;
      option.textContent = driver.driver_name;
      this.elements.driverSelect.appendChild(option);
    });

    if (currentValue !== 'all') {
      this.elements.driverSelect.value = currentValue;
    }
  }

  clearSelection() {
    this.state.selectedRows.clear();

    if (this.elements.selectAll) {
      this.elements.selectAll.checked = false;
      this.elements.selectAll.indeterminate = false;
    }

    const checkboxes = document.querySelectorAll(
      '#table-body input[type="checkbox"]'
    );
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    this.updateSelectionState();
  }

  toggleLoading(show) {
    if (this.elements.loadingOverlay) {
      this.elements.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
  }

  showToast(header, message, duration = 3000) {
    if (!this.elements.toast) return;

    const headerEl = this.elements.toast.querySelector('.toast-header');
    const bodyEl = this.elements.toast.querySelector('.toast-body');

    if (headerEl) headerEl.textContent = header;
    if (bodyEl) bodyEl.textContent = message;

    this.elements.toast.style.display = 'block';
    this.elements.toast.classList.add('show');

    setTimeout(() => {
      this.elements.toast.classList.remove('show');
      setTimeout(() => {
        this.elements.toast.style.display = 'none';
      }, 300);
    }, duration);
  }

  setModalManager(modalManager) {
    this.modalManager = modalManager;
  }
}
