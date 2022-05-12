$(document).ready(function () {
    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "System 1",
                backgroundColor: 'rgb(99,125,255)',
                borderColor: 'rgb(99,125,255)',
                data: [],
                fill: false,
            },{
                label: "System 2",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [],
                fill: false,
            },{
                label: "System 3",
                backgroundColor: 'rgb(128,255,44)',
                borderColor: 'rgb(128,255,44)',
                data: [],
                fill: false,
            },{
                label: "System 4",
                backgroundColor: 'rgb(160,44,255)',
                borderColor: 'rgb(160,44,255)',
                data: [],
                fill: false,
            }
        ],
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Messung'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                y: {
                    reverse: false,
                    max: 90,
                    min: 5,
                    ticks: {
                        stepSize: 5
                    }
                },
                x: [{
                    scaleLabel: {
                        type: 'time',
                        display: true,
                        labelString: 'Zeit'
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 100
                    }
                }]
            },
            animation: false
        },
    };


    const context = document.getElementById('canvas').getContext('2d');

    const lineChart = new Chart(context, config);

    const source = new EventSource("/chart-data");

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (config.data.labels.length > 20) {
            while (config.data.labels.length > 20) {
                config.data.labels.shift();
                config.data.datasets[0].data.shift();
                config.data.datasets[1].data.shift();
                config.data.datasets[2].data.shift();
                config.data.datasets[3].data.shift();

            }
        }
        for (let i = 0; i < data.length; i++) {
            config.data.labels.push(data[i].time.slice(11, 19));
            config.data.datasets[0].data.push(data[i].temp1);
            config.data.datasets[1].data.push(data[i].temp2);
            config.data.datasets[2].data.push(data[i].temp3);
            config.data.datasets[3].data.push(data[i].temp4);
        }
        lineChart.update();
    }
});


