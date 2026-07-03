/**
 * Health Risk Prediction System - Client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    initFormValidation();
    initAutoDismissAlerts();
});

/**
 * Initialize client-side form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Auto-dismiss flash alerts after 5 seconds
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
}

/**
 * Calculate BMI from height and weight inputs
 */
function initBMICalculator(heightId, weightId, bmiId) {
    const heightInput = document.getElementById(heightId);
    const weightInput = document.getElementById(weightId);
    const bmiInput = document.getElementById(bmiId);

    if (!heightInput || !weightInput || !bmiInput) {
        return;
    }

    function calculateBMI() {
        const height = parseFloat(heightInput.value);
        const weight = parseFloat(weightInput.value);

        if (height > 0 && weight > 0) {
            const heightM = height / 100;
            const bmi = (weight / (heightM * heightM)).toFixed(2);
            bmiInput.value = bmi;
        }
    }

    heightInput.addEventListener('input', calculateBMI);
    weightInput.addEventListener('input', calculateBMI);
}

/**
 * Initialize risk distribution pie chart
 */
function initRiskPieChart(canvasId, lowCount, mediumCount, highCount) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') {
        return;
    }

    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [lowCount, mediumCount, highCount],
                backgroundColor: ['#1cc88a', '#f6c23e', '#e74a3b'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Initialize monthly statistics bar chart
 */
function initMonthlyChart(canvasId, monthlyStats) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') {
        return;
    }

    const months = Object.keys(monthlyStats).sort();
    const lowData = months.map(function (m) { return monthlyStats[m]['Low Risk'] || 0; });
    const mediumData = months.map(function (m) { return monthlyStats[m]['Medium Risk'] || 0; });
    const highData = months.map(function (m) { return monthlyStats[m]['High Risk'] || 0; });

    if (months.length === 0) {
        months.push('No Data');
        lowData.push(0);
        mediumData.push(0);
        highData.push(0);
    }

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Low Risk',
                    data: lowData,
                    backgroundColor: '#1cc88a'
                },
                {
                    label: 'Medium Risk',
                    data: mediumData,
                    backgroundColor: '#f6c23e'
                },
                {
                    label: 'High Risk',
                    data: highData,
                    backgroundColor: '#e74a3b'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
