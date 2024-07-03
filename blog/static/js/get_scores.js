let form_scores = document.querySelector('#form_scores');

if (form_scores) {
    form_scores.addEventListener('submit', get_scores);
}

async function get_scores(e) {
    e.preventDefault();

    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    let form_data = new FormData();
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/get_scores/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();
        console.log(result);

        if (result.response) {
            document.querySelector('#user_scores').innerHTML = result.scores;
            document.querySelector('#user_unearned_scores').innerHTML = '';
            form_scores.remove();
        }
    } else {
        alert('Backend error');
    }
}