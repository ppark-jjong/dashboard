// apiService.js
class ApiService {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.sessionToken = localStorage.getItem('sessionToken');
  }

  getAuthHeaders() {
    return this.sessionToken
      ? {
          Authorization: this.sessionToken,
        }
      : {};
  }

  validateDashboardParams(params) {
    const validatedParams = { ...params };

    if (validatedParams.page) {
      validatedParams.page = Math.max(1, parseInt(validatedParams.page));
    }

    if (validatedParams.limit) {
      validatedParams.limit = Math.min(
        100,
        Math.max(1, parseInt(validatedParams.limit))
      );
    }

    if (validatedParams.driver_id && validatedParams.driver_id !== 'all') {
      validatedParams.driver_id = parseInt(validatedParams.driver_id);
    }

    return validatedParams;
  }

  parseDashboardItem(item) {
    return {
      ...item,
      eta: item.eta ? new Date(item.eta) : null,
      depart_time: item.depart_time ? new Date(item.depart_time) : null,
      completed_time: item.completed_time
        ? new Date(item.completed_time)
        : null,
    };
  }

  async request(endpoint, options = {}) {
    try {
      const url = new URL(`${this.baseURL}${endpoint}`);

      if (options.params) {
        Object.keys(options.params).forEach((key) => {
          if (options.params[key] !== 'all' && options.params[key] !== '') {
            url.searchParams.append(key, options.params[key]);
          }
        });
      }

      const fetchOptions = {
        method: options.method || 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      };

      if (options.body) {
        fetchOptions.body = JSON.stringify(options.body);
      }

      const response = await fetch(url, fetchOptions);

      // Handle 401 Unauthorized globally
      if (response.status === 401) {
        this.sessionToken = null;
        localStorage.removeItem('sessionToken');
        window.location.href = '/login.html';
        throw new Error('인증이 필요합니다.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          message: errorData.detail || '알 수 없는 오류가 발생했습니다.',
          raw: errorData,
        };
      }

      const data = await response.json();
      return {
        success: true,
        data,
        status: response.status,
      };
    } catch (error) {
      console.error(`API 호출 중 오류: ${endpoint}`, error);
      throw {
        status: error.status || 500,
        message: error.message || '서버 연결에 실패했습니다.',
        raw: error,
      };
    }
  }

  async requestWithRetry(endpoint, options = {}, retries = 3, delay = 1000) {
    let lastError;

    for (let i = 0; i < retries; i++) {
      try {
        return await this.request(endpoint, options);
      } catch (error) {
        lastError = error;

        // Don't retry on client errors
        if (error.status >= 400 && error.status < 500) {
          throw error;
        }

        if (i === retries - 1) {
          throw error;
        }

        console.log(`Retrying request (${i + 1}/${retries}) after ${delay}ms`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        // Exponential backoff
        delay *= 2;
      }
    }
  }

  // Auth Methods
  async login(userId, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: { user_id: userId, password },
    });

    if (response.success && response.data.session_token) {
      this.sessionToken = response.data.session_token;
      localStorage.setItem('sessionToken', response.data.session_token);
    }

    return response;
  }

  async logout() {
    try {
      await this.request('/auth/logout', {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });
    } finally {
      this.sessionToken = null;
      localStorage.removeItem('sessionToken');
    }
  }

  async checkAuth() {
    try {
      return await this.request('/auth/protected', {
        headers: this.getAuthHeaders(),
      });
    } catch (error) {
      this.sessionToken = null;
      localStorage.removeItem('sessionToken');
      throw error;
    }
  }

  // Dashboard Methods
  async getDashboardList(params = {}) {
    const validatedParams = this.validateDashboardParams(params);
    const response = await this.requestWithRetry('/dashboard', {
      params: validatedParams,
      headers: this.getAuthHeaders(),
    });

    if (response.data?.data) {
      response.data.data = response.data.data.map((item) =>
        this.parseDashboardItem(item)
      );
    }

    return response.data;
  }

  async refreshDashboard() {
    const response = await this.requestWithRetry('/dashboard/refresh', {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async assignDriver(driverId, dpsList) {
    if (!Array.isArray(dpsList) || dpsList.length === 0) {
      throw new Error('배송건을 선택해주세요.');
    }

    if (!driverId) {
      throw new Error('기사를 선택해주세요.');
    }

    const response = await this.requestWithRetry('/dashboard/assignDriver', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: {
        driver_id: parseInt(driverId),
        dpsList,
      },
    });
    return response.data;
  }

  async updateStatus(dps, newStatus) {
    if (!dps) {
      throw new Error('DPS 정보가 없습니다.');
    }

    if (!['대기', '진행', '완료', '이슈'].includes(newStatus)) {
      throw new Error('올바르지 않은 상태값입니다.');
    }

    const response = await this.requestWithRetry(`/dashboard/${dps}/status`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: { new_status: newStatus },
    });
    return response.data;
  }

  async getDrivers(params = {}) {
    const response = await this.requestWithRetry('/drivers', {
      params,
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }

  async getDashboardDetail(dps) {
    if (!dps) {
      throw new Error('DPS 정보가 없습니다.');
    }

    const response = await this.requestWithRetry(`/dashboard/${dps}/detail`, {
      headers: this.getAuthHeaders(),
    });
    return response.data;
  }
  async createDashboard(data) {
    const response = await this.requestWithRetry('/dashboard', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: {
        ...data,
        status: '대기', // 상태는 자동으로 '대기'로 설정
      },
    });
    return response.data;
  }
  async deleteDashboards(dpsList) {
    const response = await this.requestWithRetry('/dashboard/delete', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: { dpsList },
    });
    return response.data;
  }
}

// Create and export API service instance
export const apiService = new ApiService('http://localhost:8000');
