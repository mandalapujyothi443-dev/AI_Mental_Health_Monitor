const canvas = document.getElementById("trendChart");
if (canvas && typeof Chart !== "undefined") {
    new Chart(canvas, {
        type: "line",
        data: {
            labels: [...labels].reverse(),
            datasets: [{
                label: "Distress Indicator (%)",
                data: [...values].reverse(),
                tension: 0.25,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { min: 0, max: 100 }
            }
        }
    });
}
