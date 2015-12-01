$(document).ready(function () {
	// Load tooltips
	$('[data-toggle="tooltip"]').tooltip()

    // Change the row color if the user checks the checkmark.
    $("input[type='checkbox']").change(function (e) {
        // If it is checked and has the correct class attached to it, add the class info to it to change color.
        if ($(this).is(":checked") && $(this).hasClass("record_table")) {
            $(this).closest('tr').addClass("info");
        // If it is not checked, remove the info class.
        } else if ($(this).hasClass("record_table")) {
            $(this).closest('tr').removeClass("info");
        }
    });

    // Change expand arrow when clicking.
    $(".expand-services").click(function() {

        // Get the tag for the element that is being collapsed.
        var collapse_element = $(this).attr('href');

        // Make sure that the icon is not swapped while the animation is running.
        if ($(this).find('i').hasClass('fa-chevron-right') && $('td').find(collapse_element).hasClass('collapse')) {
            $(this).find('i').removeClass('fa-chevron-right');
            $(this).find('i').addClass('fa-chevron-down');
        } else if ($(this).find('i').hasClass('fa-chevron-down') && $('td').find(collapse_element).hasClass('collapse')) {
            $(this).find('i').removeClass('fa-chevron-down');
            $(this).find('i').addClass('fa-chevron-right');
        }
    });
});