var edit_form = document.querySelector('#edit-form');

edit_form.addEventListener('submit', edit_profile);

async function edit_profile(e) {
    e.preventDefault();

    var username = document.querySelector('input[name="username"]');
    var first_name = document.querySelector('input[name="first_name"]');
    var email = document.querySelector('input[name="email"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    var obj = new Object();
    obj.username = username.value;
    obj.first_name = first_name.value;
    obj.email = email.value;
    var form_data = JSON.stringify(obj);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/edit_profile/';

    var response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        var result = await response.json();

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/my/profile');
        } else {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            if (result.username) {
                username.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.username}</div>`);
            }
            if (result.email) {
                email.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.email}</div>`);
            }
            if (result.first_name) {
                first_name.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.first_name}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}