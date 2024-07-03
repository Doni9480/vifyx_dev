document.querySelector('#form_blog').addEventListener('submit', function(e) {
    e.preventDefault();
});

document.querySelector('#id_publish').addEventListener('click', send_blog);

async function send_blog(e) {
    e.preventDefault();

    var preview = document.querySelector('input[name="preview"');
    var title = document.querySelector('input[name="title"]');
    var level_two = document.querySelector('input[name="level_two"]');
    var level_three = document.querySelector('input[name="level_three"]');
    var level_four = document.querySelector('input[name="level_four"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    var is_private = document.querySelector('input[name="is_private"]');

    var form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }

    form_data.append('title', title.value);

    if (level_two) {
        form_data.append('level_two', level_two.value);
    }

    if (level_three) {
        form_data.append('level_three', level_three.value);
    }

    if (level_four) {
        form_data.append('level_four', level_four.value);
    }

    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    if (is_private.checked) {
        form_data.append('is_private', true);
    } else {
        form_data.append('is_private', false);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/create/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        var result = await response.json();
        console.log(result);

        form_errors = document.querySelectorAll('#form-error');

        for (const form_error of form_errors) {
            form_error.remove();
        }

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/blogs/show/' + result.slug + '/');
        } else {
            if (result.preview) {
                preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            }

            if (result.title) {
                title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            }

            if (result.level_two) {
                level_two.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_two}</div>`);
            }

            if (result.level_three) {
                level_three.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_three}</div>`);
            }

            if (result.level_four) {
                level_four.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_four}</div>`);
            }

            if (result.is_private) {
                is_private.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.is_private}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}
