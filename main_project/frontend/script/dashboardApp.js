import { apiService } from './apiService.js';
import { dashboardController } from './dashboardController.js';
import { dashboardView } from './dashboardView.js';
export default class DashboardApp {
  constructor() {
    this.currentPage = 0;
    this.pageSize = 15;
    this.selectedRows = new Set();
    this.totalPages = 0;

    this.filters = {
      status: 'all',
      driver: 'all',
      search: '',
    };

    this.initializeEventListeners();
    this.modalManager = new ModalManager(this);
    this.refreshData();
  }

  // 공통 API 호출 메서드
  async apiCall(url, method = 'GET', body = null) {
    try {
      const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
      };

      if (body) options.body = JSON.stringify(body);

      const response = await fetch(url, options);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API 호출 중 오류: ${url}`, error);
      throw error;
    }
  }

  // 로딩 오버레이 관리
  toggleLoadingOverlay(show = false) {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
      loadingOverlay.style.display = show ? 'flex' : 'none';
    }
  }

  // 이벤트 리스너 초기화
  initializeEventListeners() {
    document.getElementById('search-input')?.addEventListener('input', (e) => {
      this.filters.search = e.target.value;
      this.refreshData();
    });

    document
      .getElementById('status-filter')
      ?.addEventListener('change', (e) => {
        this.filters.status = e.target.value;
        this.refreshData();
      });

    document
      .getElementById('driver-select')
      ?.addEventListener('change', (e) => {
        this.filters.driver = e.target.value;
        this.refreshData();
      });

    document
      .getElementById('refresh-btn')
      ?.addEventListener('click', () => this.refreshData(true));

    document.getElementById('prev-page')?.addEventListener('click', () => {
      if (this.currentPage > 0) {
        this.currentPage--;
        this.refreshData();
      }
    });

    document.getElementById('next-page')?.addEventListener('click', () => {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++;
        this.refreshData();
      }
    });

    document
      .getElementById('select-all')
      ?.addEventListener('change', this.handleSelectAll.bind(this));

    document.getElementById('assign-btn')?.addEventListener('click', () => {
      const waitingSelectedDps = this.getWaitingSelectedDps();
      this.modalManager.showDriverAssignModal(waitingSelectedDps);
    });
  }

  // 전체 선택 핸들러
  handleSelectAll(e) {
    const isChecked = e.target.checked;
    const checkboxes = document.querySelectorAll(
      '#table-body input[type="checkbox"]'
    );

    checkboxes.forEach((checkbox) => {
      checkbox.checked = isChecked;
      const rowId = checkbox.getAttribute('data-row-id');

      if (isChecked) {
        this.selectedRows.add(rowId);
      } else {
        this.selectedRows.delete(rowId);
      }

      this.updateRowStyle(checkbox.closest('tr'), isChecked);
    });

    this.updateAssignButton();
  }

  // 데이터 새로고침
  async refreshData(showLoading = false) {
    try {
      this.toggleLoadingOverlay(showLoading);

      const queryParams = new URLSearchParams();

      if (this.filters.status !== 'all') {
        queryParams.append('status', this.filters.status);
      }

      if (this.filters.driver !== 'all') {
        queryParams.append('driver_id', this.filters.driver);
      }

      queryParams.append('page', this.currentPage + 1);
      queryParams.append('limit', this.pageSize);

      const response = await this.apiCall(`/api/dashboard?${queryParams}`);

      if (!response || !response.data) {
        this.showToast('알림', '조회할 데이터가 없습니다.');
        this.updateTable([]);
        return;
      }

      this.totalPages = Math.ceil(response.totalCount / this.pageSize);
      this.filteredData = response.data;

      this.updateTable(response.data);
      this.updatePagination(response.totalCount);
      this.updateDriverOptions();

      if (showLoading) {
        this.showToast('성공', '데이터가 새로고침되었습니다.');
      }
    } catch (error) {
      console.error('Detailed error:', error);
      this.showToast('실패', '데이터 로드 중 오류가 발생했습니다.');
      this.updateTable([]);
    } finally {
      this.toggleLoadingOverlay(false);
    }
  }

  // 기사 할당 가능한 DPS 목록
  getWaitingSelectedDps() {
    return Array.from(this.selectedRows).filter((dps) => {
      const item = this.filteredData.find((d) => d.dps === dps);
      return item && item.status === '대기';
    });
  }

  // 기사 할당 메서드
  async assignDriverToDps(dpsList, driverId) {
    try {
      const response = await this.apiCall('/api/assignDriver', 'POST', {
        driver_id: driverId,
        dpsList: dpsList,
      });

      return response.success;
    } catch (error) {
      console.error(error);
      return false;
    }
  }

  // 상태 변경 메서드
  async updateItemStatus(item, newStatus) {
    try {
      const response = await this.apiCall(
        `/api/dashboard/${item.dps}/status`,
        'PUT',
        {
          new_status: newStatus,
        }
      );

      return response.success;
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  // 기사 목록 업데이트
  async updateDriverOptions() {
    try {
      const response = await this.apiCall('/api/drivers');
      const drivers = response.drivers;

      this.updateDriverSelect(drivers);
      this.updateDriverAssignDropdown(drivers);
    } catch (error) {
      console.error('드라이버 목록 로드 오류:', error);
    }
  }

  // 기사 선택 드롭다운 업데이트
  updateDriverSelect(drivers) {
    const select = document.getElementById('driver-select');
    if (!select) return;

    const currentValue = select.value;
    select.innerHTML = '<option value="all">전체 기사</option>';

    drivers.forEach((driver) => {
      const option = document.createElement('option');
      option.value = driver.id;
      option.textContent = driver.name;
      select.appendChild(option);
    });

    if (currentValue !== 'all') {
      select.value = currentValue;
    }
  }

  // 기사 할당 드롭다운 업데이트
  updateDriverAssignDropdown(drivers) {
    const assignDropdown = document.getElementById('driver-assign-dropdown');
    if (!assignDropdown) return;

    assignDropdown.innerHTML = '<option value="">기사를 선택하세요</option>';

    drivers.forEach((driver) => {
      const option = document.createElement('option');
      option.value = driver.id;
      option.textContent = driver.name;
      assignDropdown.appendChild(option);
    });
  }

  // 테이블 업데이트
  updateTable(data = []) {
    const tbody = document.getElementById('table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!Array.isArray(data) || data.length === 0) {
      const noDataRow = document.createElement('tr');
      noDataRow.innerHTML = `<td colspan="12" class="text-center">조회된 데이터가 없습니다.</td>`;
      tbody.appendChild(noDataRow);
      return;
    }

    data.forEach((item) => {
      const row = this.createTableRow(item);
      tbody.appendChild(row);
    });

    this.updateSelectAllState();
  }

  // 테이블 행 생성
  createTableRow(item) {
    const row = document.createElement('tr');
    const status = ['대기', '진행', '완료', '이슈'].includes(item.status)
      ? item.status
      : '대기';
    row.classList.add(`row-${status}`);

    const location = `${item.city || item.region || ''} ${
      item.district || ''
    }`.trim();

    row.innerHTML = `
      <td class="col-checkbox">
        <label class="custom-checkbox">
          <input type="checkbox" data-row-id="${item.dps}">
          <span class="checkbox-mark"></span>
        </label>
      </td>
      <td class="col-department">${item.department || '-'}</td>
      <td class="col-type">${item.type || '-'}</td>
      <td class="col-warehouse">${item.warehouse || '-'}</td>
      <td class="col-driver">${item.driver_name || '-'}</td>
      <td class="col-dps">${item.dps || '-'}</td>
      <td class="col-sla">${item.sla || '-'}</td>
      <td class="col-eta">${item.eta || '-'}</td>
      <td class="col-status">
        <span class="status-pill status-${status}">${status}</span>
      </td>
      <td class="col-location">${location || '-'}</td>
      <td class="col-customer">${item.customer || '-'}</td>
      <td class="col-contact">${item.contact || '-'}</td>
    `;

    const checkbox = row.querySelector('input[type="checkbox"]');
    checkbox.addEventListener('change', (e) => {
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

    row.addEventListener('click', (e) => {
      if (!e.target.closest('.custom-checkbox')) {
        this.modalManager.showDetailModal(item);
      }
    });

    return row;
  }

  // 행 스타일 업데이트
  updateRowStyle(row, isSelected) {
    ['row-대기', 'row-진행', 'row-완료', 'row-이슈'].forEach((statusClass) => {
      row.classList.remove(statusClass);
    });

    const statusElement = row.querySelector('.col-status .status-pill');
    if (statusElement) {
      const status = statusElement.textContent.trim();
      if (status && ['대기', '진행', '완료', '이슈'].includes(status)) {
        row.classList.add(`row-${status}`);
      }
    }

    row.classList.toggle('selected', isSelected);
  }

  // 전체 선택 상태 업데이트
  updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('select-all');
    if (!selectAllCheckbox) return;

    const checkboxes = document.querySelectorAll(
      '#table-body input[type="checkbox"]'
    );
    const checkedCount = document.querySelectorAll(
      '#table-body input[type="checkbox"]:checked'
    ).length;

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

  // 기사 할당 버튼 상태 업데이트
  updateAssignButton() {
    const assignButton = document.getElementById('assign-btn');
    if (!assignButton) return;

    const waitingSelectedRows = this.getWaitingSelectedDps();
    assignButton.disabled = waitingSelectedRows.length === 0;
    assignButton.classList.toggle(
      'btn-disabled',
      waitingSelectedRows.length === 0
    );
  }

  // 페이지네이션 업데이트
  updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / this.pageSize);
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');

    if (prevBtn) prevBtn.disabled = this.currentPage === 0;
    if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages - 1;
    if (pageInfo)
      pageInfo.textContent = `${this.currentPage + 1} / ${totalPages}`;
  }

  // 토스트 메시지
  showToast(header, message) {
    const toast = document.getElementById('notification-toast');
    const toastHeader = toast?.querySelector('.toast-header');
    const toastBody = toast?.querySelector('.toast-body');

    if (!toast || !toastHeader || !toastBody) return;

    toastHeader.textContent = header;
    toastBody.textContent = message;

    toast.style.display = 'block';
    toast.classList.add('show');

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        toast.style.display = 'none';
      }, 300);
    }, 3000);
  }
}
