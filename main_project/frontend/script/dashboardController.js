import { apiService } from './apiService.js';
import { dashboardView } from './dashboardView.js';

export const dashboardController = {
    initialize: function () {
        console.log(`[dashboardController] 초기화됨`);
        const refreshButton = document.getElementById('refresh-btn');
        if (refreshButton) {
            refreshButton.addEventListener('click', this.refreshData);
            console.log(`[dashboardController] 리프레시 버튼 이벤트 리스너 등록됨`);
        } else {
            console.error(`[dashboardController] 리프레시 버튼을 찾을 수 없음`);
        }
    },

    async refreshData() {
        console.log(`[dashboardController] 데이터 갱신 시작`);
        try {
            const response = await apiService.get('/api/dashboard', { page: 1, limit: 15 });
            if (response && Array.isArray(response.data)) {
                console.log(`[dashboardController] 데이터 갱신 성공: ${JSON.stringify(response.data)}`);
                dashboardView.renderTable(response.data);
            } else {
                console.error(`[dashboardController] 잘못된 응답 형식: ${JSON.stringify(response)}`);
            }
        } catch (error) {
            console.error(`[dashboardController] 데이터 갱신 중 오류 발생: ${error.message}`);
        }
    },
};
