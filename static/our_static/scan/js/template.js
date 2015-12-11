$(document).ready(function () {
	// Load tooltips
	$('[data-toggle="tooltip"]').tooltip()

    // Change the row color if the user checks the checkmark.
    $("input[type='checkbox']").change(function (e) {
        // If it is checked and has the correct class attached to it, add the class info to it to change color.
        if ($(this).is(":checked") && $(this).hasClass("check-network")) {
            if ($(this).attr('num-hosts') != "0") {
                $(this).closest('tr').addClass("warning");
            } else {
                $(this).closest('tr').addClass("info");
            }
        // If it is not checked, remove the info class.
        } else if ($(this).hasClass("check-network")) {
            if ($(this).attr('num-hosts') != "0") {
                $(this).closest('tr').removeClass("warning");
            } else {
                $(this).closest('tr').removeClass("info");
            }
        }
    });

     $('#check-all-networks').click(function() {
       if($(this).is(':checked')) {
           $('.check-network').each(function(e) {
              $(this).prop('checked', true);
                if ($(this).attr('num-hosts') != "0") {
                    $(this).closest('tr').addClass("warning");
                } else {
                    $(this).closest('tr').addClass("info");
                }
           });
       } else {
           $('.check-network').each(function(e) {
              $(this).prop('checked', false);
                if ($(this).attr('num-hosts') != "0") {
                    $(this).closest('tr').removeClass("warning");
                } else {
                    $(this).closest('tr').removeClass("info");
                }
           });
       }
    });

    $('.remove-network-link').click(function(e) {
        e.preventDefault();

        $('#network-to-remove').html($(this).attr('remove-network'));
        $('#network_id').val($(this).attr('remove-network-id'))
        $('#remove-network').modal('toggle');
    });

    $('#scan-network-submit').click(function(e){
        e.preventDefault();
        var warning = false;

        $('.check-network').each(function() {
            if ($('.check-network').is(":checked")) {
                if($(this).attr('num-hosts') != '0'){
                    console.log($(this).attr('num-hosts'))
                    warning = true;
                }
                if (warning == true) {
                $('#scan-network-warning').modal('toggle');
                }
                else {
                    $("#scan-network-form").unbind('submit').submit();
                }
            }
        });
    });


    $('#scan-network-warning-submit').click(function() {
        $("#scan-network-form").unbind('submit').submit();
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

    $("#add-site-form").submit(function(e) {
        e.preventDefault();

        var site;
        site = $('#add-site-input').val();

        $.get('/site/checksite/', {site_name: site}, function(data) {
            if (data == "False") {
                $('#add-site-form-group').animate().removeClass('has-error');
                $('#add-site-error').slideUp();
                $("#add-site-form").unbind('submit').submit();
            } else {
                $('#add-site-form-group').animate().addClass('has-error');
                $('#add-site-error').slideDown();
            }
        });
    });

    $("#add-network-form").submit(function(e) {
        e.preventDefault();

        var network_address;
        var subnet_bits;
        network_address = $('#add-network-input-address').val();
        subnet_bits = $('#add-network-input-subnet').val();

        $.get('/scan/checknetwork/', {network: network_address, subnet: subnet_bits}, function(data) {
            if (data == "False") {
                $('#add-network-form-group').animate().removeClass('has-error');
                $('#add-network-error').slideUp();
                $("#add-network-form").unbind('submit').submit();
            } else {
                $('#add-network-form-group').animate().addClass('has-error');
                $('#add-network-error').slideDown();
            }
        });
    });
});