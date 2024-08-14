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

    let album = document.querySelector('input[name="album_id"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/' + album + '/hide_album/';

    let response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });

    get_g_token();

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

    let album = document.querySelector('input[name="album_id"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/' + album + '/show_album/';

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
        } else if (result.ban) {
            document.querySelector('#form_show').insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        }
    } else {
        alert('Backend error');
    }
}