let form_survey = document.querySelector('#form_survey');

form_survey.addEventListener('submit', survey_edit);

async function survey_edit(e) {
    e.preventDefault();

    let survey_id = document.querySelector('input[name="survey_id"]').value;

    let preview = document.querySelector('input[name="preview"');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let content = document.querySelector('#id_content');
    let answers = document.querySelectorAll('input[name="answers"]');
    let tags = document.querySelectorAll('input[name="tags"]');
    let level_access = document.querySelector('#id_level_access');
    let category = document.querySelector('#id_category');
    let subcategory = document.querySelector('#id_subcategory');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    tags_list = [];
    let is_empty_tags = true;
    tags.forEach(tag => {
        is_empty_tags = false;
        tags_list.push(tag.value);
    });

    answers_list = []
    answers.forEach(answer => {
        if (! answer.id) {
            answers_list.push({'title': answer.value});
        } else {
            answers_list.push({
                'title': answer.value,
                'id': answer.id,
            });
        }
    });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('description', description.value);
    form_data.append('content', content.value);
    if (answers_list) {
        form_data.append('answers_set', JSON.stringify(answers_list));
    }
    if (level_access && !isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
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
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/surveys/' + survey_id + '/update/';

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
        console.log(result);

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/surveys/show/' + result.slug);
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

            if (result.content) {
                content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            }

            if (result.category) {
                category.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.category}</div>`);
            }

            if (result.subcategory) {
                subcategory.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.subcategory}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
            
            if (result.level_access) {
                level_access.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_access}</div>`);
            }

            if (result.answers) {
                document.querySelector('#title_answers').insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.answers}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}
