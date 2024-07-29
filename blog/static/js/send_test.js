document.querySelector('#form_post').addEventListener('submit', function(e) {
    e.preventDefault();
});

// document.querySelector('#id_publish').addEventListener('click', send_post);
document.querySelector('#id_save').addEventListener('click', send_test);

async function send_test() {
    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let content = document.querySelector('#id_content');
    let language = document.querySelector('#id_language');
    let category = document.querySelector('#id_category');
    let subcategory = document.querySelector('#id_subcategory');
    let level_access = document.querySelector('#id_level_access');
    let tags = document.querySelectorAll('input[name="tags"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let blog = document.querySelector('input[name="blog"]');

    tags_list = [];
    let is_empty_tags = true;
    tags.forEach(tag => {
        is_empty_tags = false;
        tags_list.push(tag.value);
    });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    if (title) {
        form_data.append('title', title.value);
    }
    if (description) {
        form_data.append('description', description.value);
    }
    if (content) {
        form_data.append('content', content.value);
    }
    if (language.value == 'english' || language.value == 'russian') {
        form_data.append('language', language.value);
    }
    if (category && ! isNaN(Number(category.value))) {
        form_data.append('category', category.value);
    }
    if (subcategory && ! isNaN(Number(subcategory.value))) {
        form_data.append('subcategory', subcategory.value);
    }
    if (! is_empty_tags) {
        form_data.append('tags', tags_list);
    }
    if (level_access && !isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
    }
    form_data.append('blog', blog.value);
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/create/';

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

        if (result.success) {
            form_successes = document.querySelectorAll('#form-success');

            for (const form_success of form_successes) {
                form_success.remove();
            }

            document.querySelector('#id_save').insertAdjacentHTML('beforebegin', `<div id="form-success" style="color: green;">Successfully saved!</div>`);
        } else {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}


async function send_post(e) {
    e.preventDefault();

    let preview = document.querySelector('input[name="preview"');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let content = document.querySelector('#id_content');
    let language = document.querySelector('#id_language');
    let tags = document.querySelectorAll('input[name="tags"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    tags_list = [];
    let is_empty_tags = true;
    tags.forEach(tag => {
        is_empty_tags = false;
        tags_list.push(tag.value);
    });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('description', description.value);
    form_data.append('content', content.value);
    form_data.append('language', language.value);
    if (! is_empty_tags) {
        form_data.append('tags', tags_list);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/create';

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

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/posts/show/' + result.slug);
        } else if (result.ban) {
            window.scrollTo(0, 0);
            
            form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
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

            if (result.content) {
                content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            }

            if (result.language) {
                language.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.language}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}
