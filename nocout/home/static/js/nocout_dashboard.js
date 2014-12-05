$(document).ready(function(e) {
	
    /*Pie Charts*/

    var series = Math.floor(Math.random() * 9) + 1;
    series = 3;
    var pieChartLegends = [];
    var pie_color_array = ["#99CC00", "#FFE90D", "#FF0022"];
    
    pieChartLegends.push("Good");
    pieChartLegends.push("Warning");
    pieChartLegends.push("Critical");


    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("ptp_pie_chart",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("ptp_pie_chart2",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("ptp_pie_chart3",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("ptp_pie_chart4",chartData);


    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("pmp_pie_chart",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("pmp_pie_chart3",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("pmp_pie_chart4",chartData);


    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("wimax_pie_chart",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("wimax_pie_chart3",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("wimax_pie_chart4",chartData);


    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("other_pie_chart",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("other_pie_chart3",chartData);

    var chartData = getPieChartData(series,pieChartLegends,pie_color_array);
    createPieChart("other_pie_chart4",chartData);

    /*Hide Highcharts.com Name*/
    // var highcharts_link = $("#dashboard_pie_chart svg text:last-child");
    // $.grep(highcharts_link,function(val) {
    //     if($.trim(val.innerHTML) == 'Highcharts.com') {
    //         val.innerHTML = "";
    //     }
    // });
    // $(".dashboard_pie_chart svg text:last-child").hide();
    


    /*Sparkline Bar Charts*/

    $(".sparkline-bar").each(function() {

		var barSpacing, barWidth, color, height;
		color = $(this).attr("data-color");
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

    /*Sparkline Line Charts*/

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

    /*Area Chart(Uptime)*/

    var area_chart_points = 30;
    var areaChartLegends = ["PTP","PMP","WIMAX","OTHERS"];
    var areaColorArray = ["#7cb5ec","#f7a35c","#8085e9","#90ed7d"]
    var uptime_lineChart_data = getAreaChartData(area_chart_points,areaChartLegends,areaColorArray);

	createAreaChart("uptime_line_chart",uptime_lineChart_data);

	/*Initialize CEM data-table*/
	$("#cem_table").DataTable();
	$("#events_table").DataTable();
	$("#pmp_events_table").DataTable();
    $("#wimax_events_table").DataTable();
});


/**
 * This function creates pie chart data.
 * @method getPieChartData
 * @param valuesCount "Int", It contains an integer value which tells that how many data items are needed.
 * @param pieChartLegends [Array], It contains the chart legends name array.
 * @param colorArray [Array], It contains the chart color name array.
 */
function getPieChartData(valuesCount,pieChartLegends,colorArray) {

	var data = [];
	for (var i = 0; i < valuesCount; i++) {
        data[i] = {
            name: pieChartLegends[i],
            color : colorArray[i],
            y: Math.floor(Math.random() * 100),
            sliced : false,
            selected : false
        }
    }

    return data;
}

/**
 * This function creates area chart data.
 * @method getAreaChartData
 * @param valuesCount "Int", It contains an integer value which tells that how many data items are needed.
 * @param chartLegends [Array], It contains the chart legends name array.
 * @param colorArray [Array], It contains the chart color name array.
 */
function getAreaChartData(valuesCount,chartLegends,colorArray) {
    var data = [];
    for (var i = 0; i < chartLegends.length; i++) {
        var obj = {};
        obj["name"] =  chartLegends[i];
        obj["color"] = colorArray[i];
        var dataVal = [];
        for(var j=0;j<valuesCount;j++) {
            
            dataVal.push([j+1, Math.floor(Math.random() * 100)]);
        }
        obj["data"] =  dataVal;
        data[i] = obj;
    }

    return data;
}

/**
 * This function will create area chart with given data on given DOM element.
 * @uses highcharts
 * @method createAreaChart
 * @param domElement "String", It contains the div id on which the chart is to be plotted.
 * @param chartData [JSON Object Array], It contains the chart data json object array.
 */
function createAreaChart(domElement,chartData) {

    $('#'+domElement).highcharts({
        chart: {
            events: {
                load : function() {
                    // Hide highcharts.com link from chart when chart is loaded
                    var highcharts_link = $("#"+domElement+" svg text:last-child");
                    $.grep(highcharts_link,function(val) {
                        if($.trim(val.innerHTML) == 'Highcharts.com') {
                            val.innerHTML = "";
                        }
                    });
                }
            },
            type: 'areaspline'
        },
        title: {
            text: ''
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: 0,
            y: 0,
            floating: true,
            borderWidth: 1,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
        },
        tooltip: {
            shared: true,
            valueSuffix: ' units',
            useHTML : true            
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            areaspline: {
                fillOpacity: 0.5
            }
        },
        series: chartData
    });
}


/**
 * This function will create pie chart with given data on given DOM element.
 * @uses highcharts
 * @method createPieChart
 * @param domElement "String", It contains the div id on which the chart is to be plotted.
 * @param chartData [JSON Object Array], It contains the chart data json object array.
 */
function createPieChart(domElement,chartData) {

    $('#'+domElement).highcharts({
        chart: {
            events: {
                load : function() {
                    // Hide highcharts.com link from chart when chart is loaded
                    var highcharts_link = $("#"+domElement+" svg text:last-child");
                    $.grep(highcharts_link,function(val) {
                        if($.trim(val.innerHTML) == 'Highcharts.com') {
                            val.innerHTML = "";
                        }
                    });
                }
            },
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: true
        },
        series: [{
            type: 'pie',
            data: chartData
        }],
        legend:{
            enabled: true,
            x : '-20',
            y : '-20',
            floating: true,
            itemStyle: {
                color: '#555555',
                fontWeight: 'normal',
                fontSize : '12px',
                fontWeight : '400'
            }
        },
        title: {
            text: ''
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            }
        }
    });
}