document.querySelector('#form_survey').addEventListener('submit', function(e) {
    e.preventDefault();
});

let is_private = document.querySelector('input[name="checkbox-10"]');

document.querySelector('#id_publish').addEventListener('click', send_survey);
document.querySelector('#id_save').addEventListener('click', send_draft_survey);

async function send_survey(e) {
    e.preventDefault();

    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let content = document.querySelector('#id_content');
    let answers = document.querySelectorAll('input[name="answers"]');
    let tags = document.querySelectorAll('input[name="tags"]');
    let level_access = document.querySelector('#id_level_access');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let blog = document.querySelector('input[name="blog"]');

    tags_list = [];
    tags.forEach(tag => {
        tags_list.push(tag.value);
    });

    answers_list = [];
    answers.forEach(answer => {
        answers_list.push(answer.value);
    });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('description', description.value);
    form_data.append('content', content.value);
    if (level_access) {
        form_data.append('level_access', level_access.value);
    }
    if (answers_list) {
        form_data.append('answers', answers_list);
    }
    form_data.append('tags', tags_list);
    form_data.append('blog', blog.value);
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/surveys/create/';

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
            window.location.replace(window.location.protocol + '//' + window.location.host + '/surveys/show/' + result.slug);
        } else if (result.ban) {
            form_survey.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
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

            if (result.recaptcha) {
                form_survey.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }

            if (result.level_access) {
                level_access.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_access}</div>`);
            }

            if (result.blog) {
                blog.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.blog}</div>`);
            }

            if (result.answers) {
                document.querySelector('#title_answers').insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.answers}</div>`);
            }
        }
        
    } else {
        alert('Backend error');
    }
}

async function send_draft_survey(e) {
    e.preventDefault();

    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let content = document.querySelector('#id_content');
    let answers = document.querySelectorAll('input[name="answers"]');
    let tags = document.querySelectorAll('input[name="tags"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let level_access = document.querySelector('#id_level_access');
    let blog = document.querySelector('input[name="blog"]');
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    tags_list = [];
    tags.forEach(tag => {
        tags_list.push(tag.value);
    });

    answers_list = []
    answers.forEach(answer => {
        if (! answer.id) {
            answers_list.push(answer.value);
        }
    });

    let edit_answers = {};
    answers.forEach(answer => {
        if (answer.id) {
            edit_answers[answer.id] = answer.value;
        }
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
    if (! isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
    }
    if (blog) {
        form_data.append('blog', blog.value);
    }
    if (answers_list) {
        form_data.append('answers', answers_list);
    }
    if (edit_answers) {
        form_data.append('edit_answers', JSON.stringify(edit_answers));
    }
    if (tags_list) {
        form_data.append('tags', tags_list);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/drafts_survey/create/';

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
                form_survey.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}