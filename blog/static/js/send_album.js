document.querySelector('#form_album').addEventListener('submit', function(e) {
    e.preventDefault();
});

document.querySelector('#id_publish').addEventListener('click', send_album);
document.querySelector('#id_save').addEventListener('click', send_draft_album);


async function send_album(e) {
    e.preventDefault();

    var preview = document.querySelector('input[name="preview"');
    var title = document.querySelector('input[name="title"]');
    var description = document.querySelector('#id_description');
    var photos = document.querySelectorAll('input[name="photo"]');
    var language = document.querySelector('#id_language');
    var level_access = document.querySelector('#id_level_access');
    var category = document.querySelector('#id_category');
    var subcategory = document.querySelector('#id_subcategory');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    var blog = document.querySelector('input[name="blog"]');

    var form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    if (level_access && !isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
    }
    form_data.append('description', description.value);
    for (const photo of photos) {
        if (photo.files[0]) {
            form_data.append("photos_set", photo.files[0]);
        }
    }
    form_data.append('blog', blog.value);
    form_data.append('language', language.value);
    if (category && ! isNaN(Number(category.value))) {
        form_data.append('category', category.value);
    }
    if (subcategory && ! isNaN(Number(subcategory.value))) {
        form_data.append('subcategory', subcategory.value);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    var url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/create/';

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
            window.location.replace(window.location.protocol + '//' + window.location.host + '/albums/show/' + result.slug);
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

            if (result.photos_set) {
                photos[0].insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.photos_set}</div>`);
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

            if (result.blog) {
                blog.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.blog}</div>`);
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}

async function send_draft_album() {
    let preview = document.querySelector('input[name="preview"]');
    let title = document.querySelector('input[name="title"]');
    let description = document.querySelector('#id_description');
    let photos = document.querySelectorAll('input[name="photo"]');
    let deleted_photos = document.querySelectorAll('input[name="deleted_photo"]');
    let level_access = document.querySelector('#id_level_access');
    let language = document.querySelector('#id_language');
    let category = document.querySelector('#id_category');
    let subcategory = document.querySelector('#id_subcategory');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let blog = document.querySelector('input[name="blog"]');  
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

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
    if (photos) {
        for (const photo of photos) {
            if (photo.files[0]) {
                form_data.append("photos_set", photo.files[0]);
            }
        }
    }
    let deleted_photos_list = [];
    let is_empty_deleted_photos = true;
    for (const deleted_photo of deleted_photos) {
        is_empty_deleted_photos = false;
        deleted_photos_list.push({'id': deleted_photo.value});
    }
    if (! is_empty_deleted_photos) {
        form_data.append('deleted_photos_set', JSON.stringify(deleted_photos_list));
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
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/draft/create/';

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