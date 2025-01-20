class ApiService {
  constructor(baseURL) {
      this.baseURL = baseURL;
      console.log(`[apiService] 초기화됨: baseURL=${baseURL}`);
  }

  async get(endpoint, params = {}) {
      const url = new URL(`${this.baseURL}${endpoint}`);
      Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

      console.log(`[apiService] GET 요청 시작: URL=${url}`);
      try {
          const response = await fetch(url, {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
          });

          if (!response.ok) {
              console.error(`[apiService] GET 요청 실패: ${response.statusText}`);
              return null;
          }

          const data = await response.json();
          console.log(`[apiService] GET 요청 성공: 데이터=${JSON.stringify(data)}`);
          return data;
      } catch (error) {
          console.error(`[apiService] GET 요청 중 오류 발생: ${error.message}`);
          return null;
      }
  }
}

export const apiService = new ApiService('http://localhost:8000');
