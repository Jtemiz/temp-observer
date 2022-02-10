$(document).ready(function () {
    var annotation1 = {
        type: 'line',
        scaleID: 'y',
        value: 5,
        borderColor: 'red',
        borderWidth: 3,
        label: {
          backgroundColor: 'red',
          content: 'Grenzwert',
          enabled: true
        },
        click: function({chart, element}) {
            var input = prompt("Grenzwerte ändern", annotation1.value + 'mm');
            if ((parseInt(input) < config.options.scales.y.max)) {
                annotation1.value = parseInt(input);
                lineChart.update()
                $.post("/changeLimitVal", {
                    limVal: parseInt(input)
                });
            }
        }
      };


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
                        //steps 1, 2, 3, 4, 8, 10, 12, 15, 20
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
            animation: true
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
            config.data.labels.push(data[i].time);
            config.data.datasets[0].data.push(data[i].temp1);
            config.data.datasets[1].data.push(data[i].temp2);
            config.data.datasets[2].data.push(data[i].temp3);
            config.data.datasets[3].data.push(data[i].temp4);
        }
        lineChart.update();
    }
    $.post("/changeLimitVal", {
        limVal: parseInt(annotation1.value)
    });

});

$('#startBtn').on('click', function (e) {
    e.preventDefault()
    var dis = document.getElementById('distCounter').innerHTML;
    $.post("/setMeasurementDistance", {
        distance: parseFloat(dis)
    })
    $.getJSON('/toggleMeasuring',
        function (data) {
            toggleMeasuringBtn(data);
        });
});

$(document).ready(function () {
    $.getJSON('/isMActive',
        function (data) {
            toggleMeasuringBtn(data);
        });
    $.getJSON('/isPActive',
        function(data) {
            togglePauseBtn(data);
        })
})

function toggleMeasuringBtn(mIsActive) {
    if (mIsActive) {
        //messung gestartet
        $('#pauseBtn').removeAttr("hidden");
        $('#startImg').attr("hidden", true);
        $('#stopImg').removeAttr("hidden");
        $('.collapse').collapse("show");
        $('#startPauseImg').removeAttr('hidden');
        $('#stopPauseImg').attr('hidden', true);
    } else {
        $('#pauseBtn').attr("hidden", true);
        $("#stopImg").attr("hidden", true);
        $("#startImg").removeAttr("hidden");
        $('.collapse').collapse("hide");
    }
}

$('#pauseBtn').on('click', function(e) {
    e.preventDefault()
    $.getJSON('/togglePause',
        function(data) {
            togglePauseBtn(data)
        });
})

function togglePauseBtn(pIsActive){
    if (pIsActive) {
        $('#stopPauseImg').removeAttr('hidden');
        $('#startPauseImg').attr('hidden', true);
    } else {
        $('#startPauseImg').removeAttr('hidden');
        $('#stopPauseImg').attr('hidden', true);
    }
}

function setMetadata() {
    var username = document.getElementById('userMetaData').value;
    var loc = document.getElementById('locationMetaData').value;
    var meas = document.getElementById('measureMetaData').value;
    var wid = document.getElementById('widthMetaData').value;

    if (username == '') {
        username = 'Nicht angegeben'
    };
    if (loc == '') {
        loc = 'Nicht angegeben'
    };
    if (meas == '') {
        meas = 'Nicht angegeben'
    };
    console.log(meas);
    $.post( "/metaDataInput", {
        user: username,
        location: loc,
        measure: meas,
        width: wid
    });
}

function insertComment(elem) {
    var com = elem.value
    var pos = document.getElementById('distCounter').innerHTML
    console.log(com + " at " + pos)
    $.post("/addComment", {
        comment: com,
        position: pos
    })
}

