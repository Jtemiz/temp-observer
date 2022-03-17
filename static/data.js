var lineChart = null;
var choosedMeasurement = "";
var storedData = []
var searchMinDate;
var searchMaxDate

function saveCSV() {
    window.location.href = `/saveCSV?from=${searchMinDate}&to=${searchMaxDate}`;
}

function deleteTable() {
    $.post("/deleteTable", {
        tablename: choosedMeasurement
    });
    window.location.href = '/data';
}

function searchValues() {
    searchMinDate = document.getElementById("SearchDateFrom").value;
    searchMaxDate = document.getElementById("SearchDateTo").value;
    $("#loading-spinner").removeAttr("hidden");
    $("#searchBtn").attr("disabled", true);
    $.get(`/searchValues?from=${searchMinDate}&to=${searchMaxDate}`,
        function (data) {
            config.data.labels = [];
            config.data.datasets[0].data = [];
            config.data.datasets[1].data = [];
            config.data.datasets[2].data = [];
            config.data.datasets[3].data = [];
            storedData = data;
            for (let i = 0; i < data.metaData.dataSize; i++) {
                config.data.labels.push(new Date(Date.parse(data.values[i][0])).toLocaleString());
                config.data.datasets[0].data.push(data.values[i][1]);
                config.data.datasets[1].data.push(data.values[i][2]);
                config.data.datasets[2].data.push(data.values[i][3]);
                config.data.datasets[3].data.push(data.values[i][4]);
            }
            lineChart.update();
            $("#openChartBtn").removeAttr("hidden");
            $("#createPDFBtn").removeAttr("hidden");
            $("#createCSVBtn").removeAttr("hidden");
            $("#loading-spinner").attr("hidden", true);
            $("#searchBtn").removeAttr("disabled");
        });
}


var timeFormat = 'DD/MM/YYYY';

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
        }, {
            label: "System 2",
            backgroundColor: 'rgb(255, 99, 132)',
            borderColor: 'rgb(255, 99, 132)',
            data: [],
            fill: false,
        }, {
            label: "System 3",
            backgroundColor: 'rgb(128,255,44)',
            borderColor: 'rgb(128,255,44)',
            data: [],
            fill: false,
        }, {
            label: "System 4",
            backgroundColor: 'rgb(160,44,255)',
            borderColor: 'rgb(160,44,255)',
            data: [],
            fill: false,
        }
        ],
    },
    options: {
        spanGaps: true,
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
                    type: 'datetime',
                    display: true,
                    labelString: 'Zeit',
                    time: {
                        format: timeFormat,
                        tooltipFormat: 'll'
                    },
                },
                ticks: {
                    autoSkip: true,
                    maxTicksLimit: 100
                }
            }]
        },
        animation: false,
        plugins: {
            zoom: {
                zoom: {
                    wheel: {
                        enabled: true,
                    },
                    drag: {
                        enabled: true
                    },
                    mode: 'x',
                },
                options: {
                    transitions: {
                        zoom: {
                            animation: {
                                duration: 0
                            }
                        }
                    }
                }
            },
            decimation: {
                enabled: true,
                algorithm: 'min-max',
                samples: 50
            },
        },
        datasets: {
            line: {
                pointRadius: 0 // disable for all `'line'` datasets
            }
        },
    },
};

$(document).ready(function () {
    const context = document.getElementById('canvas').getContext('2d');
    lineChart = new Chart(context, config);
});


var PDFHeader = [{text: 'Datum/Uhrzeit', style: 'tableHeader'}, {
    text: 'System 1',
    style: 'tableHeader'
}, {text: 'System 2', style: 'tableHeader'}, {text: 'System 3', style: 'tableHeader'}, {
    text: 'System 4',
    style: 'tableHeader'
}]


var docDefinition = {
    info: {
        title: ''
    },
    content: [],
    styles: {
        header: {
            fontSize: 16,
            bold: true,
            margin: [0, 0, 0, 10]
        },
        subheader: {
            fontSize: 16,
            bold: true,
            margin: [0, 10, 0, 5]
        },
        tableExample: {
            margin: [0, 5, 0, 15]
        },
        tableOpacityExample: {
            margin: [0, 5, 0, 15],
            fillColor: 'blue',
            fillOpacity: 0.3
        },
        tableHeader: {
            bold: true,
            fontSize: 13,
            color: 'black'
        }
    },
    defaultStyle: {
        // alignment: 'justify'
    },
    patterns: {
        stripe45d: {
            boundingBox: [1, 1, 4, 4],
            xStep: 3,
            yStep: 3,
            pattern: '1 w 0 1 m 4 5 l s 2 0 m 5 3 l s'
        }
    }
};

function createPDFDocDefinition() {
    var dd = JSON.parse(JSON.stringify(docDefinition));
    dd.info.title = `${searchMinDate}_${searchMaxDate}`
    dd.content.push(
        {
            text: `Temperaturaufzeichnung von ${searchMinDate} bis ${searchMaxDate}`,
            style: 'header'
        },
        {
            style: 'tableExample',
            table: {
                headerRows: 1,
                body: createTableBody(storedData.values, PDFHeader)
            }
        }
    );
    return dd;
}

function createTableBody(data, columns) {
    var body = [];
    body.push(columns);
    var insertableData = data[0].map((_, colIndex) => data.map(row => row[colIndex]));
    var dates = [];
    insertableData[0].forEach(date => {
        dates.push(new Date(date).toLocaleString());
    });
    insertableData[0] = dates;
    body.push(insertableData);
    return body;
}

function table(data, columns) {
    return {
        table: {
            headerRows: 1,
            body: buildTableBody(data, columns)
        }
    };
}

function openDataPDF() {
    pdfMake.createPdf(createPDFDocDefinition()).open();
}
