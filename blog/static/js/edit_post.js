let form_post = document.querySelector('#form_post');

form_post.addEventListener('submit', post_edit);

async function post_edit(e) {
    e.preventDefault();

    let post_id = document.querySelector('input[name="post_id"]').value;

    let preview = document.querySelector('input[name="preview"');
    let title = document.querySelector('input[name="title"]');
    let content = document.querySelector('#id_content');
    let add_survey = document.querySelector('input[name="add_survey"]');
    let answers = document.querySelectorAll('input[name="answers"]');
    let tags = document.querySelectorAll('input[name="tags"]');
    let level_access = document.querySelector('#id_level_access');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    tags_list = [];
    tags.forEach(tag => {
        tags_list.push(tag.value);
    });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    
    if (add_survey.checked) {
        answers_list = [];
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

        if (answers_list) {
            form_data.append('answers', answers_list);
        }
        if (edit_answers) {
            form_data.append('edit_answers', JSON.stringify(edit_answers));
        }
    }

    if (add_survey.checked) {
        answers_list = [];
        let is_empty_answers = true;
        answers.forEach(answer => {
            if (answer.value) {
                is_empty_answers = false;
                if (answer.id) {
                    answers_list.push({
                        'title': answer.value,
                        'id': answer.id,
                    });
                } else {
                    answers_list.push({
                        'title': answer.value,
                    });
                }
            }
        });

        if (! is_empty_answers) {
            form_data.append('answers_set', JSON.stringify(answers_list));
        }

        form_data.append('add_survey', 1);
    }

    if (level_access) {
        form_data.append('level_access', level_access.value);
    }

    if (add_survey.checked) {
        form_data.append('add_survey', 1);
    }

    form_data.append('title', title.value);
    form_data.append('content', content.value);
    form_data.append('tags', tags_list);
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/' + post_id + '/update/';

    let response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/posts/show/' + result.slug);
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

            if (result.level_access) {
                level_access.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_access}</div>`);
            }

            if (result.content) {
                content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            }

            if (result.answers_set) {
                document.querySelector('#title_answers').insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.answers_set}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}