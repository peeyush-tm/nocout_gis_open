/*This is a temporary code which is replace when data for data table is provided*/
$(".datatable").DataTable();

/*Code for Calender*/
var date = new Date();
var d = date.getDate();
var m = date.getMonth();
var y = date.getFullYear();

/*Initialize Calendar*/
var calendarObj = $('#scheduling_calendar').fullCalendar({
	header : {
	    left:   'prev,next today',
	    center: 'title',
		right:  'month,agendaWeek,agendaDay'
	},
	selectable : true,
	editable : true,
	select : function(start,end,allDay) {
		var title = prompt('Event Title:');
		if(title) {
			calendarObj.fullCalendar("renderEvent",
				{
					title : title,
					start : start,
					end   : end,
					allDay: allDay
				},
				true // By this the event will be sticky
			);
		}
		calendarObj.fullCalendar("unselect");
	},
	editable : true,
	droppable: true,
	drop: function(date, allDay) { // this function is called when something is dropped

		// retrieve the dropped element's stored Event Object
		var originalEventObject = $(this).data('eventObject');
		
		// we need to copy it, so that multiple events don't have a reference to the same object
		var copiedEventObject = $.extend({}, originalEventObject);
		
		// assign it the date that was reported
		copiedEventObject.start = date;
		copiedEventObject.allDay = allDay;
		
		// render the event on the calendar
		// the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
		$('#scheduling_calendar').fullCalendar('renderEvent', copiedEventObject, true);
		
		// is the "remove after drop" checkbox checked?
		if ($('#drop-remove').is(':checked')) {
			// if so, remove the element from the "Draggable Events" list
			$(this).remove();
		}
		
	},
	events: [
		{
			title: 'All Day Event',
			start: new Date(y, m, 1),
			backgroundColor: Theme.colors.blue,
		},
		{
			title: 'Long Event',
			start: new Date(y, m, d-5),
			end: new Date(y, m, d-2),
			backgroundColor: Theme.colors.red,
		}
	]
});