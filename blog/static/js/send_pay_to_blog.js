var forms = document.querySelectorAll('#form_follow');

if (forms) {
    forms.forEach(form => {
        form.addEventListener('submit', send_pay);
    });
}

async function send_pay(e) {
    e.preventDefault();

    var radios = e.target.querySelectorAll('input[type="radio"]');
    var blog_id = document.querySelector('input[name="blog_id"]').value;
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var level = e.target.querySelector('input[name="level"]').value;

    var term = null;
    radios.forEach(radio => {
        console.log(radio);
        if (radio.checked) {
            term = radio.value;
        }
    });

    var form_data = new FormData();
    form_data.append('term', term);
    form_data.append('level', level);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/pay/' + blog_id + '/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        form_errors = e.target.querySelectorAll('#form-error');

        for (const form_error of form_errors) {
            form_error.remove();
        }

        var result = await response.json();
        console.log(result);
        if (result.success) {
            window.location.reload();
        } else if (result.error_scores) {
            e.target.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.error_scores}</div>`);
        }
    } else {
        alert('Backend error');
    }
}