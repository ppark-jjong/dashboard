// visualization.js
class VisualizationApp {
    constructor() {
        this.initializeCharts();
    }

    initializeCharts() {
        this.createTimeChart();
        this.createDistrictChart();
    }

    createTimeChart() {
        const ctx = document.getElementById('timeChart').getContext('2d');

        const timeLabels = Array.from({ length: 24 }, (_, i) =>
            `${String(i).padStart(2, '0')}:00`
        );

        const mockData = Array.from({ length: 24 }, () =>
            Math.floor(Math.random() * 20) + 5
        );

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: 'Order Count',
                    data: mockData,
                    backgroundColor: 'rgba(75, 118, 229, 0.5)',
                    borderColor: 'rgba(75, 118, 229, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Orders by Time',
                        font: {
                            size: 16,
                            weight: '600'
                        },
                        padding: 20
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createDistrictChart() {
        const ctx = document.getElementById('districtChart').getContext('2d');

        const districts = MockService.districts || ['Gangnam', 'Gangdong', 'Gangseo', 'Gangbuk', 'Gwanak'];
        const mockData = Array.from({ length: districts.length }, () =>
            Math.floor(Math.random() * 20) + 10
        );

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: districts,
                datasets: [{
                    label: 'Order Count',
                    data: mockData,
                    borderColor: 'rgba(75, 118, 229, 1)',
                    backgroundColor: 'rgba(75, 118, 229, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(75, 118, 229, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Orders by District',
                        font: {
                            size: 16,
                            weight: '600'
                        },
                        padding: 20
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// 페이지 로드 시 시각화 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    new VisualizationApp();
});