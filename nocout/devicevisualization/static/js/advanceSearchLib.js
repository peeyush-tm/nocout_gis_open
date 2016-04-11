/*Global Variables*/
var advSearch_self = "",
	gmapInstance = "",
	setFilterApiUrl = "",
	earthInstance = "",
    filtersInfoArray = [],
    templateData = "",
    formElements = "",
    elementsArray = [],
    resultantObject = {},
    appliedAdvFilter = [],
    appliedAdvFilter_Active = [],
    searchParameters = "",
    lastSelectedValues = [];
    searchquery_data=[];
    result_plot_devices=[];
/**
 * This class is used to create th filter form by calling the get_filter API & the call the set_filter API with the selected filters
 * @class advanceSearchLib
 * @uses jQuery
 * Coded By :- Yogender Purohit
 */
function advanceSearchClass() {

	/*Store the reference of current pointer in a global variable*/
	advSearch_self = this;
	
	/**
	 * This function remove applied advance filter
	 * @method removeFilters
	 */	
	this.removeFilters = function() {
		
		/*Reset filter data array*/
		lastSelectedValues = [];
		appliedAdvFilter = [];
		appliedAdvFilter_Active = [];
        result_plot_device=[]

        if(!($("#advFilterContainerBlock").hasClass("hide"))) {
			$("#advFilterContainerBlock").addClass("hide");
		}

		/*Hide Remove Filters button*/
		if(!$("#removeFilterBtn").hasClass("hide")) {
			$("#removeFilterBtn").addClass("hide");
		}

        // Not to clear the html for gmap page
    	$("#filter_technology").select2("val","");
    	$("#filter_vendor").select2("val","");
    	$("#filter_state").select2("val","");
    	$("#filter_city").select2("val","");
    	$("#filter_frequency").select2("val","");
    	$("#filter_polarization").select2("val","");
    	$("#filter_antena_type").select2("val","");
    	// Reset Advance Filters Flag
        isAdvanceFilter = 0;
        
		/*Call the resetVariables function to reset all global variables*/
		advSearch_self.resetVariables();

		/*Click The Refresh Button*/
		// $("#resetFilters").click();
		networkMapInstance.updateStateCounter_gmaps();
	};

	/**
	 * This function reset all variable used in the process
	 * @method resetVariables
	 */
	this.resetVariables = function() {

		/*Reset the variable*/
		filtersInfoArray = [];
		templateData = "";
		formElements = "";
		elementsArray = [];
		resultantObject = {};
		searchParameters = "";
	};
}