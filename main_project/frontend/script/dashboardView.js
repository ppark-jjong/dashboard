// dashboardView.js
export class DashboardView {
    constructor() {
        this.elements = {
            table: document.getElementById('data-table'),
            tableBody: document.getElementById('table-body'),
            searchInput: document.getElementById('search-input'),
            statusFilter: document.getElementById('status-filter'),
            driverSelect: document.getElementById('driver-select'),
            refreshBtn: document.getElementById('refresh-btn'),
            assignBtn: document.getElementById('assign-btn'),
            selectAll: document.getElementById('select-all'),
            prevPage: document.getElementById('prev-page'),
            nextPage: document.getElementById('next-page'),
            pageInfo: document.getElementById('page-info'),
            loadingOverlay: document.querySelector('.loading-overlay'),
            toast: document.getElementById('notification-toast')
        };

        // 필요한 엘리먼트 확인
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
        this.elements.searchInput?.addEventListener('input', e =>
            controller.updateFilter('search', e.target.value)
        );

        this.elements.statusFilter?.addEventListener('change', e =>
            controller.updateFilter('status', e.target.value)
        );

        this.elements.driverSelect?.addEventListener('change', e =>
            controller.updateFilter('driver', e.target.value)
        );

        // 새로고침
        this.elements.refreshBtn?.addEventListener('click', () =>
            controller.refreshData(true)
        );

        // 페이지네이션
        this.elements.prevPage?.addEventListener('click', () =>
            controller.updatePage(controller.state.currentPage - 1)
        );

        this.elements.nextPage?.addEventListener('click', () =>
            controller.updatePage(controller.state.currentPage + 1)
        );

        // 전체 선택
        this.elements.selectAll?.addEventListener('change', e => {
            const checkboxes = document.querySelectorAll('#table-body input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = e.target.checked;
                controller.updateSelection(checkbox.dataset.rowId, e.target.checked);
            });
        });
    }

    formatDate(date) {
        if (!date) return '-';
        return new Intl.DateTimeFormat('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    renderTable(data) {
        if (!this.elements.tableBody) return;

        this.elements.tableBody.innerHTML = '';

        if (!data.length) {
            this.elements.tableBody.innerHTML = `
          <tr>
            <td colspan="12" class="text-center">조회된 데이터가 없습니다.</td>
          </tr>`;
            return;
        }

        data.forEach(item => {
            const row = this.createTableRow(item);
            this.elements.tableBody.appendChild(row);
        });
    }

    createTableRow(item) {
        const row = document.createElement('tr');
        row.dataset.status = item.status;

        const location = `${item.city || item.region || ''} ${item.district || ''}`.trim();

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
        <td class="col-eta">${this.formatDate(item.eta)}</td>
        <td class="col-status">
          <span class="status-pill status-${item.status}">${item.status}</span>
        </td>
        <td class="col-location">${location || '-'}</td>
        <td class="col-customer">${item.customer || '-'}</td>
        <td class="col-contact">${item.contact || '-'}</td>
      `;

        return row;
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
        this.elements.driverSelect.innerHTML = '<option value="all">전체 기사</option>';

        drivers.forEach(driver => {
            const option = document.createElement('option');
            option.value = driver.driver;
            option.textContent = driver.driver_name;
            this.elements.driverSelect.appendChild(option);
        });

        if (currentValue !== 'all') {
            this.elements.driverSelect.value = currentValue;
        }
    }

    updateAssignButton(enabled) {
        if (this.elements.assignBtn) {
            this.elements.assignBtn.disabled = !enabled;
            this.elements.assignBtn.classList.toggle('btn-disabled', !enabled);
        }
    }

    clearSelection() {
        if (this.elements.selectAll) {
            this.elements.selectAll.checked = false;
            this.elements.selectAll.indeterminate = false;
        }

        const checkboxes = document.querySelectorAll('#table-body input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        this.updateAssignButton(false);
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
}