// dashboardController.js
export class DashboardController {
    constructor(view, apiService) {
        this.view = view;
        this.apiService = apiService;
        this.state = {
            currentPage: 1,
            pageSize: 15,
            selectedRows: new Set(),
            filters: {
                status: 'all',
                driver: 'all',
                search: ''
            }
        };
    }

    async initialize() {
        try {
            await this.refreshData();
            await this.loadDrivers();
            // 이벤트 바인딩은 view에서 처리
            this.view.bindEvents(this);
        } catch (error) {
            this.handleError(error);
        }
    }

    async refreshData(showLoading = false) {
        try {
            this.view.toggleLoading(showLoading);

            if (showLoading) {
                await this.apiService.refreshDashboard();
            }

            const params = {
                ...this.state.filters,
                page: this.state.currentPage,
                limit: this.state.pageSize
            };

            const response = await this.apiService.getDashboardList(params);

            if (!response?.data?.length) {
                this.view.showToast('알림', '조회할 데이터가 없습니다.');
                this.view.renderTable([]);
                return;
            }

            this.view.renderTable(response.data);
            this.view.updatePagination({
                currentPage: this.state.currentPage,
                totalPages: Math.ceil(response.totalCount / this.state.pageSize)
            });

            if (showLoading) {
                this.view.showToast('성공', '데이터가 새로고침되었습니다.');
            }
        } catch (error) {
            this.handleError(error);
        } finally {
            this.view.toggleLoading(false);
        }
    }

    async loadDrivers() {
        try {
            const response = await this.apiService.getDrivers();
            this.view.updateDriverOptions(response.drivers);
        } catch (error) {
            this.handleError(error, '기사 목록 로드 실패');
        }
    }

    async assignDriver(driverId, dpsList) {
        try {
            const response = await this.apiService.assignDriver(driverId, dpsList);

            if (response.success) {
                this.state.selectedRows.clear();
                this.view.clearSelection();
                await this.refreshData(true);
                this.view.showToast('성공', `${dpsList.length}건 할당 완료`);
                return true;
            }

            this.view.showToast('실패', response.message || '기사 할당 실패');
            return false;
        } catch (error) {
            this.handleError(error);
            return false;
        }
    }

    async updateStatus(dps, newStatus) {
        try {
            const response = await this.apiService.updateStatus(dps, newStatus);
            if (response.success) {
                await this.refreshData(true);
                this.view.showToast('성공', `상태가 ${newStatus}(으)로 변경되었습니다.`);
                return true;
            }
            return false;
        } catch (error) {
            this.handleError(error);
            return false;
        }
    }

    updateFilter(type, value) {
        this.state.filters[type] = value;
        this.state.currentPage = 1;  // 필터 변경시 첫 페이지로
        this.refreshData();
    }

    updatePage(page) {
        if (page < 1) return;
        this.state.currentPage = page;
        this.refreshData();
    }

    handleError(error, defaultMessage = '오류가 발생했습니다.') {
        console.error(error);
        this.view.showToast('오류', error.message || defaultMessage);
    }

    getSelectedRows() {
        return this.state.selectedRows;
    }

    updateSelection(dps, isSelected) {
        if (isSelected) {
            this.state.selectedRows.add(dps);
        } else {
            this.state.selectedRows.delete(dps);
        }
        this.view.updateAssignButton(this.state.selectedRows.size > 0);
    }
}