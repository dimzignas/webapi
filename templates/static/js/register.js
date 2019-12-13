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
            console.log('masuk fungsi register')
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
        NEW_NOTE: NEW_NOTE,
        EXISTING_NOTE: EXISTING_NOTE,
        reset: function () {
            console.log('masuk fungsi reset')
            $username.text('');
            $password.val('');
            $nama_lengkap.val('');
            $email.val('');
            $username.val('').focus();
        },
        alert: function (msg, alert_status) {
            console.log('masuk fungsi alert')
            $('.alert')
                .text(msg)
                .css('class', 'alert ' + alert_status)
                .css('visibility', 'visible');
            setTimeout(function () {
                $('.alert').fadeOut();
            }, 2000)
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
        $nama_lengkap = $('#nama_lengkap');

    // Get the data from the model after the controller is done initializing
    setTimeout(function () {
        view.reset();
    }, 100)

    // generic error handler
    function error_handler(xhr, textStatus, errorThrown) {
        console.log('masuk fungsi error handler')
        let error_msg = `${textStatus}: ${errorThrown} - ${xhr.responseJSON.detail}`;

        view.alert(error_msg, 'alert-danger');
        console.log(error_msg);
    }

    // Create our event handlers
    $('#submit').click(function (e) {
        console.log('masuk fungsi submit')
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
                view.alert('Berhasil mendaftar', 'alert-success');
                console.log(data)
            })
            .fail(function(xhr, textStatus, errorThrown) {
                error_handler(xhr, textStatus, errorThrown);
            });
        view.reset();
    });
}(ns.model, ns.view));

