var edit_form = document.querySelector('#edit-form-password');

edit_form.addEventListener('submit', edit_password);

async function edit_password(e) {
    e.preventDefault();

    var password = document.querySelector('input[name="password"]');
    var password2 = document.querySelector('input[name="password2"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    var obj = new Object();
    obj.password = password.value;
    obj.password2 = password2.value;
    var form_data = JSON.stringify(obj);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/edit_password/';

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

            if (result.password) {
                password.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.password}</div>`);
            }
            if (result.password2) {
                password2.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.password2}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}