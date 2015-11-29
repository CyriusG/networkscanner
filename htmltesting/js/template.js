$(document).ready(function () {
	// Load tooltips
	$('[data-toggle="tooltip"]').tooltip()
	
    $('.record_table tr').click(function (event) {
        if (event.target.type !== 'checkbox') {
            $(':checkbox', this).trigger('click');
        }
    });

    $("input[type='checkbox']").change(function (e) {
        if ($(this).is(":checked") && $(this).hasClass("record_table")) {
            $(this).closest('tr').addClass("info");
        } else {
            $(this).closest('tr').removeClass("info");
        }
    });
});