form_delete = document.querySelectorAll('.form-delete');
form_delete.forEach(element => {
    element.addEventListener("submit", async function(event) {
        event.preventDefault();
        let question_id = element.querySelector('input[name="question_id"]').value;
        let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]').value;
        let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
        if (window.location.pathname.startsWith('/test/')) {
            url = window.location.protocol + '//' + window.location.host + '/api/v1/test/question_delete/' + question_id + '/';
        } else if (window.location.pathname.startsWith('/posts/')) {
            url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/question/' + question_id + '/delete/';
        } else {
            url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/question/' + question_id + '/delete/';
        }
        let form_data = new FormData();
        form_data.append('g_recaptcha_response', g_recaptcha_response);
        let response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: form_data
        })
    
        get_g_token();
    
        document.querySelector('div[data-question-id="' + question_id + '"]').innerHTML = ''
    });
});