let form_hide = document.querySelector('#form_hide');
let form_show = document.querySelector('#form_show');

if (form_hide) {
    form_hide.addEventListener('submit', send_hide);
}
if (form_show) {
    form_show.addEventListener('submit', send_show);
}

async function send_hide(e) {
    e.preventDefault();

    let test = document.querySelector('input[name="test_id"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    form_data.append('hide_to_user', false);
    form_data.append('hide_to_moderator', false);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/' + test + '/visibility/';
    console.log(url);

    let response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}

async function send_show(e) {
    e.preventDefault();

    let test = document.querySelector('input[name="test_id"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    form_data.append('hide_to_user', true);
    form_data.append('hide_to_moderator', true);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/' + test + '/visibility/';
    console.log(url);

    let response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            alert(result)
            window.location.reload();
        } else if (result.ban) {
            document.querySelector('#form_show').insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        }
    } else {
        alert('Backend error');
    }
}