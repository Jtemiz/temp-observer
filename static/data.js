var lineChart = null;
var choosedMeasurement = "";

function saveCSV(tablename) {
	window.location.href = "/saveCSV/" + tablename;
}

function deleteTable() {
	$.post("/deleteTable", {
		tablename: choosedMeasurement
	});
	window.location.href ='/data';
}

function searchValues() {
	$.post("/searchValues", {
		minDate: document.getElementById("SearchDateFrom").innerHTML,
		maxDate: document.getElementById("SearchDateTo").innerHTML
	});
}

function changeChoosedMeasurement(val) {
	this.choosedMeasurement = val;
}

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
		},
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
				reverse: true,
				max: 90,
				min: 0,
				ticks: {
					stepSize: 5
				}
			},
			x: [{
				scaleLabel: {
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

$(document).ready(function () {
	const context = document.getElementById('canvas').getContext('2d');
	lineChart = new Chart(context, config);
});

function displayMeasurement(tablename) {
	$("#canvas").attr("hidden", true);
	$("#spinnerDisplayModal").removeAttr("hidden");
	$.get("/getMeasurement/" + tablename, function(data) {
		config.data.labels = []
		config.data.datasets[0].data = []
		for (let i = 0; i < data.length; i++) {
			config.data.labels.push(data[i][1]);
			config.data.datasets[0].data.push(data[i][2]);
		}
		lineChart.update();
		$("#spinnerDisplayModal").attr("hidden", true);
		$("#canvas").removeAttr("hidden");
	});
}
