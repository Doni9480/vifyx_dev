var form_level_follow = document.querySelector('#form_level_follow');

form_level_follow.addEventListener('submit', send_level_follow);

async function send_level_follow(e) {
    e.preventDefault();

    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let scores = document.querySelector('input[name="scores"]');
    let blog = document.querySelector('input[name="blog_id"]')?.value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('description', description.value);
    form_data.append('scores', scores.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/create_level_follow/' + blog + '/';

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

        form_errors = document.querySelectorAll('#form-error');

        for (const form_error of form_errors) {
            form_error.remove();
        }

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/blogs/show/' + result.slug);
        } else {
            if (result.preview) {
                preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            }

            if (result.title) {
                title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            }

            if (result.description) {
                description.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.description}</div>`);
            }

            if (result.scores) {
                scores.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.scores}</div>`);
            }
        }
        
    } else {
        alert('Backend error');
    }
}