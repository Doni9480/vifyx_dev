var form_donate = document.querySelector('#form_donate');

form_donate.addEventListener('submit', donate);

async function donate(e) {
    e.preventDefault();

    var blog_id = document.querySelector('input[name="blog_id"]').value;
    var amount = document.querySelector('input[name="amount"]');
    var message = document.querySelector('#id_message');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    let form_data = new FormData();
    form_data.append('amount', amount.value);
    form_data.append('message', message.value);
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    form_data.append('blog', blog_id);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/donate/' + blog_id + '/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });
    
    get_g_token();

    if (response.ok) {
        form_blocks = document.querySelectorAll('#form-block');

        for (const form_block of form_blocks) {
            form_block.remove();
        }

        var result = await response.json();

        if (result.success) {
            form_donate.insertAdjacentHTML('beforebegin', `<div id="form-block" style="color: green;">Success!</div>`);
        } else {
            if (result.amount) {
                amount.insertAdjacentHTML('beforebegin', `<div id="form-block" style="color: red;">${result.amount}</div>`);
            }

            if (result.message) {
                message.insertAdjacentHTML('beforebegin', `<div id="form-block" style="color: red;">${result.message}</div>`);
            }

            if (result.error_scores) {
                amount.insertAdjacentHTML('beforebegin', `<div id="form-block" style="color: red;">${result.error_scores}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}