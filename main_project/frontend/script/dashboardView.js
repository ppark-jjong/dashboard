export const dashboardView = {
  renderTable: function (data) {
      console.log(`[dashboardView] 테이블 렌더링 시작`);
      if (!Array.isArray(data) || data.length === 0) {
          console.error(`[dashboardView] 유효하지 않은 데이터: ${JSON.stringify(data)}`);
          return;
      }

      const tableBody = document.querySelector("#dashboard-table tbody");
      if (!tableBody) {
          console.error(`[dashboardView] 테이블 본문 요소를 찾을 수 없음`);
          return;
      }

      tableBody.innerHTML = ""; // 기존 데이터를 초기화
      data.forEach(item => {
          const row = document.createElement("tr");
          row.innerHTML = `
              <td>${item.department || 'N/A'}</td>
              <td>${item.type || 'N/A'}</td>
              <td>${item.warehouse || 'N/A'}</td>
              <td>${item.driver_name || 'N/A'}</td>
              <td>${item.dps || 'N/A'}</td>
              <td>${item.status || 'N/A'}</td>
          `;
          tableBody.appendChild(row);
      });

      console.log(`[dashboardView] 테이블 렌더링 완료`);
  },
};
