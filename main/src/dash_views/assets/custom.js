// 모달 관련 함수 (업데이트 완료)
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('.dash-table-container');
    tables.forEach(table => {
        table.addEventListener('click', function(e) {
            const cell = e.target.closest('td');
            if (cell) {
                const row = cell.parentNode;
                const tableId = table.closest('.data-table-container').id;
                const modalId = tableId.split('-')[0] + '-modal';

                // 선택된 행의 데이터를 모달로 전달
                const rowData = {};
                row.querySelectorAll('td').forEach((cell, index) => {
                    const column = table.querySelectorAll('th')[index].textContent;
                    rowData[column] = cell.textContent;
                });

                // 모달 내용 업데이트
                const modal = document.getElementById(modalId);
                Object.entries(rowData).forEach(([key, value]) => {
                    const element = modal.querySelector(`[data-field="${key}"]`);
                    if (element) {
                        element.textContent = value;
                    }
                });

                // 모달 표시
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    });
});

// 배차 저장 버튼 이벤트
window.saveDispatch = function(tableId, driverDropdownId, modalId) {
    const selectedDriver = document.getElementById(driverDropdownId).value;
    const table = document.getElementById(tableId);

    if (!selectedDriver || !table) return;

    const activeRow = table.querySelector('tr.active');
    if (!activeRow) return;

    // 선택된 행의 데이터 업데이트
    activeRow.querySelector('[data-field="Driver"]').textContent = selectedDriver;

    // 모달 닫기
    const modal = document.getElementById(modalId);
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
};

// 페이지네이션 함수
window.createCustomPagination = function(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const createPageButton = (pageNum, isActive = false) => {
        const button = document.createElement('button');
        button.className = `page-number ${isActive ? 'current' : ''}`;
        button.textContent = pageNum;
        button.onclick = () => onPageChange(pageNum - 1);
        return button;
    };

    const pagination = document.createElement('div');
    pagination.className = 'custom-pagination';

    // Previous 버튼
    const prevButton = document.createElement('button');
    prevButton.textContent = '이전';
    prevButton.disabled = currentPage === 0;
    prevButton.onclick = () => onPageChange(currentPage - 1);
    pagination.appendChild(prevButton);

    // 페이지 번호
    for (let i = 0; i < totalPages; i++) {
        pagination.appendChild(createPageButton(i + 1, i === currentPage));
    }

    // Next 버튼
    const nextButton = document.createElement('button');
    nextButton.textContent = '다음';
    nextButton.disabled = currentPage === totalPages - 1;
    nextButton.onclick = () => onPageChange(currentPage + 1);
    pagination.appendChild(nextButton);

    container.appendChild(pagination);
};

// 필터링 함수
window.updateTableFilters = function(tableId, filters) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    Array.from(rows).forEach(row => {
        let show = true;

        for (let [key, value] of Object.entries(filters)) {
            if (!value) continue;  // 빈 필터는 무시

            const cell = row.querySelector(`[data-field="${key}"]`);
            if (!cell) continue;

            const cellValue = cell.textContent.toLowerCase();
            if (!cellValue.includes(value.toLowerCase())) {
                show = false;
                break;
            }
        }

        row.style.display = show ? '' : 'none';
    });
};
