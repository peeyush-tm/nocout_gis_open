$(document).ready(function(e) {
	
    var series = Math.floor(Math.random() * 9) + 1;
    series = 3;
    var pieChartLegends = [];
    var pie_color_array = ["#A8BC7B", "#F0AD4E", "#D9534F"];
    
    pieChartLegends.push("Good");
    pieChartLegends.push("Warning");
    pieChartLegends.push("Critical");

    /*Draw PTP pie chart*/
    var ptp_data = getPieChartData(series,pieChartLegends);

	$.plot($("#ptp_pie_chart"), ptp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#ptp_pie_chart2"), ptp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#ptp_pie_chart3"), ptp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#ptp_pie_chart4"), ptp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

	/*Draw PMP pie chart*/
    var pmp_data = getPieChartData(series,pieChartLegends);

	$.plot($("#pmp_pie_chart"), pmp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#pmp_pie_chart3"), pmp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#pmp_pie_chart4"), pmp_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

	/*Draw Wimax pie chart*/
    var wimax_data = getPieChartData(series,pieChartLegends);

	$.plot($("#wimax_pie_chart"), wimax_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#wimax_pie_chart3"), wimax_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#wimax_pie_chart4"), wimax_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

	/*Draw Others pie chart*/
    var other_data = getPieChartData(series,pieChartLegends);

	$.plot($("#other_pie_chart"), other_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#other_pie_chart3"), other_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $.plot($("#other_pie_chart4"), other_data, {
        series: {
            pie: {
                show: true
            }
        },
		colors: pie_color_array,
		legend : {
			position : "nw"
		}
    });

    $(".sparkline-bar").each(function() {

		var barSpacing, barWidth, color, height;
		color = $(this).attr("data-color") || "#ff7f00";
		height = "18px";
		barWidth = "3px";
		barSpacing = "1px";
		return $(this).sparkline("html", {
			type: "bar",
			barColor: color,
			height: height,
			barWidth: barWidth,
			barSpacing: barSpacing,
			zeroAxis: true
		});
	});

    $(".sparkline-line").each(function() {

		var barSpacing, barWidth, color, height;
		color = $(this).attr("data-color") || "red";
		height = "18px";
		return $(this).sparkline("html", {
			type: "line",
			height: height,
			zeroAxis: false
		});
	});

    var wimax = [
                    [30, 10],
                    [29, 24],
                    [28, 38],
                    [27, 32],
                    [26, 31],
                    [25, 25],
                    [24, 35],
                    [23, 46],
                    [22, 36],
                    [21, 48],
                    [20, 38],
                    [19, 60],
                    [18, 63],
                    [17, 72],
                    [16, 58],
                    [15, 65],
                    [14, 50],
                    [13, 32],
                    [12, 40],
                    [11, 35],
                    [10, 30],
                    [9, 35],
                    [8, 50],
                    [7, 53],
                    [6, 42],
                    [5, 34],
                    [4, 22],
                    [3, 15],
                    [2, 20],
                    [1, 5]
                ];
    var pmp = [
                    [1, 0],
                    [2, 14],
                    [3, 28],
                    [4, 22],
                    [5, 21],
                    [6, 15],
                    [7, 25],
                    [8, 36],
                    [9, 26],
                    [10, 38],
                    [11, 28],
                    [12, 50],
                    [13, 53],
                    [14, 62],
                    [15, 48],
                    [16, 55],
                    [17, 40],
                    [18, 22],
                    [19, 30],
                    [20, 25],
                    [21, 20],
                    [22, 15],
                    [23, 40],
                    [24, 43],
                    [25, 32],
                    [26, 24],
                    [27, 12],
                    [28, 5],
                    [29, 19],
                    [30, 27]
                ];

    var ptp = [

                    [30, 110],
                    [29, 124],
                    [28, 138],
                    [27, 132],
                    [26, 31],
                    [25, 225],
                    [24, 135],
                    [23, 146],
                    [22, 236],
                    [21, 248],
                    [20, 238],
                    [19, 160],
                    [18, 263],
                    [17, 72],
                    [16, 158],
                    [15, 65],
                    [14, 50],
                    [13, 32],
                    [12, 40],
                    [11, 35],
                    [10, 130],
                    [9, 135],
                    [8, 150],
                    [7, 153],
                    [6, 120],
                    [5, 140],
                    [4, 220],
                    [3, 150],
                    [2, 200],
                    [1, 50]
    ]

    var others = [
                [1, 10],
                [2, 114],
                [3, 128],
                [4, 122],
                [5, 121],
                [6, 115],
                [7, 125],
                [8, 136],
                [9, 126],
                [10, 138],
                [11, 128],
                [12, 150],
                [13, 153],
                [14, 162],
                [15, 148],
                [16, 155],
                [17, 140],
                [18, 122],
                [19, 130],
                [20, 125],
                [21, 120],
                [22, 115],
                [23, 140],
                [24, 143],
                [25, 132],
                [26, 124],
                [27, 112],
                [28, 15],
                [29, 119],
                [30, 127]
            ];

	/*Line chart data*/
	var uptime_lineChart_data = [{label: 'wimax', color:'#70AFC4', data: wimax},
                                {label: 'pmp', color:'#f22f43', data: pmp},
                                {label: 'ptp', color:'#f22999', data: ptp},
                                {label: 'others', color:'#70BBB4', data: others}
    ];

	createLineChart(uptime_lineChart_data,"uptime_line_chart");

	/*Initialize CEM data-table*/
	$("#cem_table").DataTable();
	$("#events_table").DataTable();
	$("#pmp_events_table").DataTable();
    $("#wimax_events_table").DataTable();
});

function getPieChartData(series,pieChartLegends) {

	var data = [];
	for (var i = 0; i < series; i++) {
        data[i] = {
            label: pieChartLegends[i],
            data: Math.floor(Math.random() * 100)
        }
    }

    return data;
}

function createLineChart(chart_data,domElement) {

	$.plot($("#"+domElement), chart_data, {
        series: {
            lines: {
                show: true,
                lineWidth: 2,
                fill: true,
                fillColor:{
                    colors:[{opacity:0.004}, {opacity:0.003}, {opacity:0.002}, {opacity:0.001}]
                }
            }
        },
        yaxis: {},
        xaxis: {},
		grid: {
			hoverable: true,
			borderWidth: 0,
			autoHighlight: false
		}
    });
}