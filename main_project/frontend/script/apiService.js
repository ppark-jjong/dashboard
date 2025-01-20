// apiService.js
class ApiService {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    parseDashboardItem(item) {
        return {
            ...item,
            eta: item.eta ? new Date(item.eta) : null,
            depart_time: item.depart_time ? new Date(item.depart_time) : null,
            completed_time: item.completed_time ? new Date(item.completed_time) : null
        };
    }

    validateDashboardParams(params) {
        const validatedParams = { ...params };

        if (validatedParams.page) {
            validatedParams.page = Math.max(1, parseInt(validatedParams.page));
        }

        if (validatedParams.limit) {
            validatedParams.limit = Math.min(100, Math.max(1, parseInt(validatedParams.limit)));
        }

        if (validatedParams.driver_id && validatedParams.driver_id !== 'all') {
            validatedParams.driver_id = parseInt(validatedParams.driver_id);
        }

        return validatedParams;
    }

    async request(endpoint, options = {}) {
        try {
            const url = new URL(`${this.baseURL}${endpoint}`);

            if (options.params) {
                Object.keys(options.params).forEach(key => {
                    if (options.params[key] !== 'all' && options.params[key] !== '') {
                        url.searchParams.append(key, options.params[key]);
                    }
                });
            }

            const fetchOptions = {
                method: options.method || 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
            };

            if (options.body) {
                fetchOptions.body = JSON.stringify(options.body);
            }

            const response = await fetch(url, fetchOptions);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw {
                    status: response.status,
                    message: errorData.detail || '알 수 없는 오류가 발생했습니다.',
                    raw: errorData
                };
            }

            return await response.json();
        } catch (error) {
            console.error(`API 호출 중 오류: ${endpoint}`, error);
            throw {
                status: error.status || 500,
                message: error.message || '서버 연결에 실패했습니다.',
                raw: error
            };
        }
    }

    async requestWithRetry(endpoint, options = {}, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                return await this.request(endpoint, options);
            } catch (error) {
                if (i === retries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
                console.log(`Retrying request (${i + 1}/${retries})`);
            }
        }
    }

    // Dashboard API
    async getDashboardList(params = {}) {
        const validatedParams = this.validateDashboardParams(params);
        const response = await this.requestWithRetry('/api/dashboard', { params: validatedParams });

        if (response.data) {
            response.data = response.data.map(item => this.parseDashboardItem(item));
        }

        return response;
    }

    async refreshDashboard() {
        return this.requestWithRetry('/api/dashboard/refresh');
    }

    async assignDriver(driverId, dpsList) {
        if (!Array.isArray(dpsList) || dpsList.length === 0) {
            throw new Error('배송건을 선택해주세요.');
        }

        if (!driverId) {
            throw new Error('기사를 선택해주세요.');
        }

        return this.requestWithRetry('/api/assignDriver', {
            method: 'POST',
            body: {
                driver_id: parseInt(driverId),
                dpsList
            }
        });
    }

    async updateStatus(dps, newStatus) {
        if (!dps) {
            throw new Error('DPS 정보가 없습니다.');
        }

        if (!['대기', '진행', '완료', '이슈'].includes(newStatus)) {
            throw new Error('올바르지 않은 상태값입니다.');
        }

        return this.requestWithRetry(`/api/dashboard/${dps}/status`, {
            method: 'PUT',
            body: { new_status: newStatus }
        });
    }

    async getDrivers() {
        return this.requestWithRetry('/api/drivers');
    }

    async getDashboardDetail(dps) {
        if (!dps) {
            throw new Error('DPS 정보가 없습니다.');
        }
        return this.requestWithRetry(`/api/dashboard/${dps}/detail`);
    }
}

export const apiService = new ApiService('http://localhost:8000');