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
        register: function (user) {
            let ajax_options = {
                type: 'POST',
                url: '/api/v1.0/users/register',
                accepts: 'application/json',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify(user)
            };
            return $.ajax(ajax_options);
        }
    };
}());

// Create the view instance
ns.view = (function () {
    'use strict';

    let $username = $('#username'),
        $password = $('#password'),
        $email = $('#email'),
        $nama_lengkap = $('#nama_lengkap');

    // return the API
    return {
        reset: function () {
            $username.focus();
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
        $username = $('#username'),
        $password = $('#password'),
        $email = $('#email'),
        $nama_lengkap = $('#nama_lengkap'),
        $uname = $('#uname'),
        $key = $('#key'),
        $form_pre = $('#pre_data_profile');

    // Get the data from the model after the controller is done initializing
    setTimeout(function () {
        view.reset();
    }, 100);

    // generic error handler
    function error_handler(xhr, textStatus, errorThrown) {
        let error_msg = `${textStatus}: ${errorThrown} - ${xhr.responseJSON.detail}`;
        view.alert(error_msg, 'alert-danger');
    }

    // Create our event handlers
    $('#submit').click(function (e) {
        let username = $username.val(),
            password = $password.val(),
            nama_lengkap = $nama_lengkap.val(),
            email = $email.val();

        e.preventDefault();

        model.register({
            'username': username,
            'password': password,
            'nama_lengkap': nama_lengkap,
            'email': email,
        })
            .done(function(data) {
                view.alert('Berhasil mendaftar. Anda akan segera diarahkan ke halaman profil.', 'alert-success');
                $uname.val(data.username);
                $key.val(data.api_key);
                setTimeout(function () {
                    $form_pre.submit();
                }, 3000);
            })
            .fail(function(xhr, textStatus, errorThrown) {
                error_handler(xhr, textStatus, errorThrown);
            });
        view.reset();
    });
}(ns.model, ns.view));

