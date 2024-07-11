var form_post = document.querySelector('#form_blog');

form_blog.addEventListener('submit', blog_edit);

async function blog_edit(e) {
    e.preventDefault();

    var blog_id = document.querySelector('input[name="blog_id"]').value;
    var preview = document.querySelector('input[name="preview"');
    var title = document.querySelector('input[name="title"]');
    var description = document.querySelector('#id_description');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    var form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    form_data.append('description', description.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/' + blog_id + '/update/';

    var response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        var result = await response.json();

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/blogs/show/' + result.slug);
        } else {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            if (result.preview) {
                preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            }

            if (result.title) {
                title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            }

            if (result.description) {
                description.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.description}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}