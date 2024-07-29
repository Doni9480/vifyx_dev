document.querySelector('#form_post').addEventListener('submit', function(e) {
    e.preventDefault();
});

document.querySelector('#id_publish').addEventListener('click', send_post);
document.querySelector('#id_save').addEventListener('click', send_draft);

async function send_draft() {
    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let content = document.querySelector('#id_content');
    let answers = document.querySelectorAll('input[name="answers"]');
    let tags = document.querySelectorAll('input[name="tags"]');
    let level_access = document.querySelector('#id_level_access');
    let language = document.querySelector('#id_language');
    let category = document.querySelector('#id_category');
    let subcategory = document.querySelector('#id_subcategory');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let is_paid = document.querySelector('input[name="is_paid"]');
    let add_survey = document.querySelector('input[name="add_survey"]');
    let is_create_test = document.querySelector('input[name="is_create_test"]');
    let amount = document.querySelector('input[name="amount"]');
    let blog = document.querySelector('input[name="blog"]');  
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
    if (title) {
        form_data.append('title', title.value);
    }
    if (content) {
        form_data.append('content', content.value);
    }
    if (language.value == 'russian' || language.value == 'english') {
        form_data.append('language', language.value);   
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
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);
    if (blog) {
        form_data.append('blog', blog.value);
    }
    if (add_survey.checked) {
        answers_list = []
        let is_empty_answers = true;
        answers.forEach(answer => {
            if (answer.value) {
                is_empty_answers = false;
                if (! answer.id) {
                    answers_list.push({'title': answer.value});
                } else {
                    answers_list.push({
                        'title': answer.value,
                        'id': answer.id,
                    });
                }
            } 
        });

        if (! is_empty_answers) {
            form_data.append('answers_set', JSON.stringify(answers_list));
        }

        form_data.append('add_survey', 1);
    }
    if (! is_empty_tags) {
        form_data.append('tags', tags_list);
    }
    if (is_paid.checked && amount) {
        form_data.append('is_paid', 1);
        if (amount) {
            form_data.append('amount', amount.value);
        }
    }
    if (is_create_test.checked) {
        form_data.append('is_create_test', true);
    } else {
        form_data.append('is_create_test', false);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/draft/create/';

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
    let content = document.querySelector('#id_content');
    let answers = document.querySelectorAll('input[name="answers"]');
    let language = document.querySelector('#id_language');
    let tags = document.querySelectorAll('input[name="tags"]');
    let level_access = document.querySelector('#id_level_access');
    let add_survey = document.querySelector('input[name="add_survey"]');
    let is_create_test = document.querySelector('input[name="is_create_test"]');
    let category = document.querySelector('#id_category');
    let subcategory = document.querySelector('#id_subcategory');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let is_paid = document.querySelector('input[name="is_paid"]');
    let amount = document.querySelector('input[name="amount"]');
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
    form_data.append('title', title.value);
    form_data.append('content', content.value);
    if (level_access && !isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
    }

    if (add_survey.checked) {
        answers_list = [];
        let is_empty_answers = true;
        answers.forEach(answer => {
            if (answer.value) {
                is_empty_answers = false;
                answers_list.push({'title': answer.value});
            }
        });

        if (! is_empty_answers) {
            form_data.append('answers_set', JSON.stringify(answers_list));
        }

        form_data.append('add_survey', 1);
    }

    if (! is_empty_tags) {
        form_data.append('tags', tags_list);
    }
    form_data.append('blog', blog.value);

    if (is_paid.checked && amount) {
        form_data.append('is_paid', 1);
        form_data.append('amount', amount.value);
    }

    if (is_create_test.checked) {
        form_data.append('is_create_test', 1);
    }

    form_data.append('language', language.value);
    if (category && ! isNaN(Number(category.value))) {
        form_data.append('category', category.value);
    }
    if (subcategory && ! isNaN(Number(subcategory.value))) {
        form_data.append('subcategory', subcategory.value);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    let url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/create/';

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

            if (result.content) {
                content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            }

            if (result.language) {
                language.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.language}</div>`);
            }
            
            if (result.category) {
                category.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.category}</div>`);
            }

            if (result.subcategory) {
                subcategory.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.subcategory}</div>`);
            }

            if (result.level_access) {
                level_access.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.level_access}</div>`);
            }

            if (result.is_paid) {
                is_paid.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.is_paid}</div>`);
            }

            if (result.amount) {
                amount.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.amount}</div>`);
            }

            if (result.add_survey) {
                add_survey.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.add_survey}</div>`);
            }

            if (result.is_create_test) {
                is_create_test.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.is_create_test}</div>`);
            }

            if (result.blog) {
                blog.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.blog}</div>`);
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
