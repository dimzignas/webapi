/*
 * JavaScript file for the application to demonstrate
 * using the API for the People SPA
 */

// Create the namespace instance
let ns = {};

// Create the model instance
ns.model = (function () {
    'use strict';

    // Return the API
    return {
        read: function (username, api_key) {
            let ajax_options = {
                type: 'GET',
                url: '/api/v1.0/users/' + username + '?api_key=' + api_key,
                accepts: 'application/json',
                dataType: 'json'
            };
            return $.ajax(ajax_options);
        }
    };
}());

// Create the view instance
ns.view = (function () {
    'use strict';

    var $table_body = $('table tbody');

    // return the API
    return {
        build_table: function (data) {
            var html = ''
            $.each(data, function(key, value) {
                html += '<tr><td>' + key + '</td><td>' + value + '</td></tr>'
            });

            // Append the rows to the table tbody
            $table_body.append(html);
        },
        alert: function (msg, alert_status) {
            $('.alert')
                .text(msg)
                .attr('class', 'alert ' + alert_status)
                .css('visibility', 'visible')
				.css('display', 'block');
            setTimeout(function () {
                $('.alert').fadeOut();
            }, 8000);
        }
    };
}());

// Create the controller
ns.controller = (function (m, v) {
    'use strict';

    let model = m,
        view = v,
        $uname = $('#uname').val(),
        $key = $('#key').val();

    // Get the data from the model after the controller is done initializing
    setTimeout(function () {
        model.read($uname, $key)
            .done(function (data) {
                view.build_table(data);
            })
            .fail(function (xhr, textStatus, errorThrown) {
                error_handler(xhr, textStatus, errorThrown);
            });
    }, 100);

    // generic error handler
    function error_handler(xhr, textStatus, errorThrown) {
        let error_msg = `${textStatus}: ${errorThrown} - ${xhr.responseJSON.detail}`;
        view.alert(error_msg, 'alert-danger');
    }
}(ns.model, ns.view));

