var csrf_token = '{{ csrf_token }}';

// FIXME: not using these, can remove
//$(document).ready(function(){
//    $('[data-toggle="tooltip"]').tooltip(); 
//});

function is_valid_json(data) {
    try {
       response = jQuery.parseJSON(data);
       return true;
    } catch {
       return false;
    }
}

function no_validate_form_hack() {
    $("#editForm").attr('novalidate', 'novalidate');
}

function do_post(url, csrf) {
    data = {
        'csrfmiddlewaretoken' : csrf
    };
    var req = $.post(url, data, function() {
    })
    .done(function() {
        location.reload()
    })
    .fail(function(err) {
        alert(err.responseText);
    })
    .always(function() {
    });
}

function confirm_post(url, prompt, csrf) {
    var answer = confirm(prompt)
    if (answer) {
        do_post(url, csrf);
    }
}