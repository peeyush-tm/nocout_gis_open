

// Method for pie Chart
function highcharts_piechart(url, domElement) {
    $.ajax({
        url : url,
        type : "GET",
        success : function(result) {
            var response = "";
            if(typeof result == 'string') {
                response = JSON.parse(result);
            } else {
                response = result;
            }

            if(response.success==1) {
                // Pie Chart Color(Use default colors if API doesn't pass any color list)
                var default_chart_colors = window.Highcharts.getOptions().colors,
                    colors_list = response.data.objects.chart_data[0].color ? response.data.objects.chart_data[0].color : default_chart_colors;

                var pie_chart = $(domElement).highcharts({
                    chart: {
                        events: {
                            load : function() {
                                // Hide highcharts.com link from chart when chart is loaded
                                var highcharts_link = $(domElement+" svg text:last-child");
                                $.grep(highcharts_link,function(val) {
                                    if($.trim(val.innerHTML) == 'Highcharts.com') {
                                        val.innerHTML = "";
                                    }
                                });
                            }
                        },
                        plotBackgroundColor: null,
                        plotBorderWidth: null,
                        plotShadow: false
                    },
                    title: {
                        // text: response.data.objects.chart_data[0].title
                        text: ""
                    },
                    legend:{
                        itemDistance : 15,
                        itemMarginBottom : 5,
                        // itemWidth : 138,
                        borderColor : "#CCCCCC",
                        borderWidth : "1",
                        borderRadius : "8",
                        itemStyle: {
                            color: '#555555',
                            fontSize : '10px'
                        }
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
                    },
                    series: [{
                        type: 'pie',
                        name: response.data.objects.chart_data[0].name,
                        colors: colors_list,
                        data: response.data.objects.chart_data[0].data
                    }],
                    lang: {
                        noData: 'Data is not available.'
                    },
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    },
                });
            }else{
                $(domElement).html("<h5>Dashboard Setting is not available.</h5>");
            }
        },
    }); // ajax
}

/* End of method pie Chart */

/* method for Area Spline Chart
highcharts_areachart(url, domElement); */
function highcharts_areachart(url, domElement) {
    $.ajax({
        url : url,
        type : "GET",
        success : function(result) {
            var response = "";
            if(typeof result == 'string') {
                response = JSON.parse(result);
            } else {
                response = result;
            }

            if(response.success == 1) {

                $(domElement).highcharts({
                    chart: {
                        events: {
                            load : function() {
                                // Hide highcharts.com link from chart when chart is loaded
                                var highcharts_link = $(domElement+" svg text:last-child");
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
                        // text: 'MFR Processed'
                        text: ''
                    },
                    legend: {
                        itemDistance : 15,
                        itemMarginBottom : 5,
                        // borderColor : "#FFF",
                        borderWidth : "1",
                        borderRadius : "5",
                        itemStyle: {
                            // color: '#FFF',
                            fontSize : '12px'
                        }
                    },
                    yAxis: {
                        title: {
                            text: 'Process Values'
                        }
                    },
                    xAxis: {
                        title: {
                            text: "Month"
                        },
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            millisecond: '%H:%M:%S.%L',
                            second: '%H:%M:%S',
                            minute: '%H:%M',
                            hour: '%H:%M',
                            day: '%e. %b',
                            week: '%e. %b',
                            month: '%b \'%y',
                            year: '%Y'
                        }
                    },
                    tooltip: {
                        headerFormat: '{point.x:%e/%m/%Y (%b)  %l:%M %p}<br>',
                        pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b><br/>',
                        shared: true,
                        crosshairs: true,
                        useHTML: true,
                        valueSuffix: response.data.objects.chart_data[0].valuesuffix
                    },
                    series: response.data.objects.chart_data[0].data,
                    lang: {
                        noData: 'Data is not available.'
                    },
                    noData: {
                        style: {
                            fontWeight: 'bold',
                            fontSize: '20px',
                            color: '#539fb8',
                        }
                    },
                });
            } else {
                $(domElement).html("<h5>Dashboard Setting is not available.</h5>");
            }
        }
    });
}
/* End of method Area Spline Chart */

// function for getting speedometer charts through ajax request.
function get_speedometer_chart(ajax_url, div_id, div_text){

    $.ajax({
        url : ajax_url,
        type : "GET",
        success : function(result) {
            var response = "";
            if(typeof result == 'string') {
                response = JSON.parse(result);
            } else {
                response = result;
            }
            if (response.success==1){
                var gaugeOptions = {
                    chart: {
                        events: {
                            load : function() {
                                // Hide highcharts.com link from chart when chart is loaded
                                var highcharts_link = $(div_id+" svg text:last-child");
                                $.grep(highcharts_link,function(val) {
                                    if($.trim(val.innerHTML) == 'Highcharts.com') {
                                        val.innerHTML = "";
                                    }
                                });
                            }
                        },
                        type: 'solidgauge'
                    },
                    // title: null,
                    title: "",
                    pane: {
                        center: ['50%', '85%'],
                        size: '140%',
                        startAngle: -90,
                        endAngle: 90,
                        background: {
                            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
                            innerRadius: '60%',
                            outerRadius: '100%',
                            shape: 'arc'
                        }
                    },
                    tooltip: {
                        enabled: false
                    },

                    // the value axis
                    yAxis: {
                        stops: [
                            [0.0, response.data.objects.chart_data[0].data[0].color], // speedometer_color
                        ],
                        lineWidth: 0,
                        minorTickInterval: null,
                        tickPixelInterval: 400,
                        tickWidth: 0,
                        tickPositions:[1,10],
                        title: {
                            y: -70
                        },
                        labels: {
                            y: 16
                        }
                    },
                    plotOptions: {
                        solidgauge: {
                            dataLabels: {
                                y: 5,
                                borderWidth: 0,
                                useHTML: true
                            }
                        }
                    }
                };

                $(div_id).highcharts(Highcharts.merge(gaugeOptions, {
                    yAxis: {
                        min: 1,
                        max: 10,
                        title: {
                            // text: div_text
                            text: ""
                        }
                    },

                    series: [{
                        name: div_text,
                        data: [response.data.objects.chart_data[0].data[0].count],
                        dataLabels: {
                        format: '<div style="text-align:center"><span style="font-size:25px;color:' +
                            ((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">{y:1f}</span><br/>' +
                            '</div>'
                        },
                        lang: {
                            noData: 'Data is not available.'
                        },
                        tooltip: {
                            valueSuffix: ' revolutions/min'

                        }
                    }]
                }));
            }else{
                $(div_id).html("<h5>Dashboard Setting is not available.</h5>");

            }
        },
        error : function(err) {
            hideSpinner();
            $.gritter.add({
                // (string | mandatory) the heading of the notification
                title: div_title,
                // (string | mandatory) the text inside the notification
                text: err.statusText,
                // (bool | optional) if you want it to fade out on its own or just sit there
                sticky: false,
                // Time in ms after which the gritter will dissappear.
                time : 1500
            });
        },
    });
}
