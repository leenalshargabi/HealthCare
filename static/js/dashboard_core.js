// dashboard_core.js - Essential Dashboard Logic
document.addEventListener("DOMContentLoaded", function () {
    
    // 1. Initialize Chart only if the canvas exists
    const chartCanvas = document.getElementById('dynamicChart');
    
    if (chartCanvas && typeof chartData !== 'undefined') {
        const ctx = chartCanvas.getContext('2d');
        
        // Destroy existing chart instance if it exists to prevent memory leaks
        if (window.myHospitalChart) {
            window.myHospitalChart.destroy();
        }

        window.myHospitalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels, // المتغيرات القادمة من بايثون
                datasets: [{
                    label: 'Operations Count',
                    data: chartData.values,
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.05)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 3,
                    pointBackgroundColor: '#4e73df'
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: { 
                        beginAtZero: true,
                        ticks: { stepSize: 1 } // لأن عدد العمليات أرقام صحيحة
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
});

// 2. Global Helper for Form Auto-submit (Optional but useful)
function autoSubmit(formId) {
    document.getElementById(formId).submit();
}