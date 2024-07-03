var is_notificated = document.querySelector('input[name="is_notificated"]');

is_notificated.addEventListener('change', send_is_notificated);

async function send_is_notificated(e) {
    e.preventDefault();

    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    var form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    if (is_notificated.checked) {
        form_data.append('is_notificated', true);
    } else {
        form_data.append('is_notificated', false);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/is_notificated/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });

    get_g_token();

    if (! response.ok) {
        alert('Backend error');
    }
}