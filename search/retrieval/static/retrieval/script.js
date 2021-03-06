
$(function() {
    $( "#date-start" ).datepicker();
});

$(function() {
    $( "#date-end" ).datepicker();
});

function toggleDateElements() {
    if(document.getElementById('date-start').disabled == false){
        document.getElementById('date-start').disabled = true;
        document.getElementById('date-end').disabled = true;
    } else {
        document.getElementById('date-start').disabled = false;
        document.getElementById('date-end').disabled = false;
    }
}

function isValidDate(dateString)
{
    // First check for the pattern
    if(!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString))
        return false;

    // Parse the date parts to integers
    var parts = dateString.split("/");
    var day = parseInt(parts[1], 10);
    var month = parseInt(parts[0], 10);
    var year = parseInt(parts[2], 10);

    // Check the ranges of month and year
    if(year < 1000 || year > 3000 || month == 0 || month > 12 || month < 0)
        return false;

    var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];

    // Adjust for leap years
    if(year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
        monthLength[1] = 29;

    // Check the range of the day
    return day > 0 && day <= monthLength[month - 1];
};

function validateForm() {
    var dateStart = document.forms["searchForm"]["date_start"].value;
    var dateEnd = document.forms["searchForm"]["date_end"].value;

    if(isValidDate(dateStart) == false || isValidDate(dateEnd) == false) {
        alert("Please provide valid dates in mm/dd/yyyy format");
        return false;
    }

    if(new Date(dateEnd) < new Date(dateStart)){
        alert("End date can not be before start date")
        return false;
    }

    if(new Date(dateStart) > Date.now()){
        alert("Please select a start date in the past, there is no news from the future")
        return false;
    }
}