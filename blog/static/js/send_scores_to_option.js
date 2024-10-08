let form_scores_to_option = document.querySelector('#form_scores_to_option');

if (form_scores_to_option) {
    form_scores_to_option.addEventListener('submit', send_scores);
}

async function send_scores(e) {
    e.preventDefault();

    let radios = document.querySelectorAll('input[name="radio-group-2"]');

    let option_id = null;
    radios.forEach(radio => {
        if (radio.checked) {
            option_id = radio.value;
        }
    });

    if (option_id) {
        let scores = form_scores_to_option.querySelector('input[name="scores"]');
        let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
        let csrftoken = form_scores_to_option.querySelector('input[name="csrfmiddlewaretoken"]').value;
        let survey_id = document.querySelector('input[name="survey_id"]')?.value;
        let post_id = document.querySelector('input[name="post_id"]')?.value;
    
        let form_data = new FormData();
        form_data.append('scores', scores.value);
        form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    
        if (post_id) {
            url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/send_scores_to_option/' + option_id + '/';
        } else if (survey_id) {
            url = window.location.protocol + '//' + window.location.host + '/api/v1/surveys/send_scores_to_option/' + option_id + '/';
        }
    
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
                form_scores_to_option.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.error_scores}</div>`);
            } else if (result.success) {
                window.location.reload();
            } else {
                if (result.recaptcha) {
                    form_scores_to_option.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
                }

                if (result.scores) {
                    form_scores_to_option.insertAdjacentHTML('afterbegin', `<div id="form-error" style="color: red;">${result.scores}</div>`);
                }
            }  
    
     
        } else {
            alert('Backend error');
        }
    }
}