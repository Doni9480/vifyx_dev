var is_autorenewal = document.querySelector('input[name="is_autorenewal"]');

is_autorenewal.addEventListener('change', send_is_autorenewal);

async function send_is_autorenewal(e) {
    e.preventDefault();

    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    var form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    if (is_autorenewal.checked) {
        form_data.append('is_autorenewal', true);
    } else {
        form_data.append('is_autorenewal', false);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/is_autorenewal/';

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