let form_scores = document.querySelector('#form_scores');

if (form_scores) {
    form_scores.addEventListener('submit', send_scores);
}


async function send_scores(e) {
    e.preventDefault();
    
    let post_id = document.querySelector('input[name="post_id"]').value;
    let scores = form_scores.querySelector('input[name="scores"]');
    let csrftoken = form_scores.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    if (scores) {
        form_data.append('scores', scores.value);
    }


    url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/' + post_id + '/send_scores/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        form_errors = document.querySelectorAll('#form-error');
        for (const form_error of form_errors) {
            form_error.remove();
        }

        if (result.error_scores) {
            form_scores.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.error_scores}</div>`);
        } else if (result.success) {

            if (result.scores) {
                document.querySelector('#post_scores').innerHTML = result.scores;
                scores.value = '';
            }
        } else {
            if (result.recaptcha) {

                form_scores.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }

            if (result.scores) {
                form_scores.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.scores}</div>`);
            }
        }

    } else {
        alert('Backend error');
    }
}