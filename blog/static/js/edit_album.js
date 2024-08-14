var form_album = document.querySelector('#form_album');

form_album.addEventListener('submit', album_edit);

async function album_edit(e) {
    e.preventDefault();

    var album_id = document.querySelector('input[name="album_id"]').value;

    var preview = document.querySelector('input[name="preview"');
    var title = document.querySelector('input[name="title"]');
    var photos = document.querySelectorAll('input[name="photo"]');
    var deleted_photos = document.querySelectorAll('input[name="deleted_photo"]');
    var category = document.querySelector('#id_category');
    var subcategory = document.querySelector('#id_subcategory');
    var level_access = document.querySelector('#id_level_access');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    var form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }

    if (level_access && !isNaN(Number(level_access.value))) {
        form_data.append('level_access', level_access.value);
    }

    form_data.append('title', title.value);
    for (const photo of photos) {
        if (photo.files[0]) {
            form_data.append("photos_set", photo.files[0]);
        }
    }
    var deleted_photos_list = [];
    var is_empty_deleted_photos = true;
    for (const deleted_photo of deleted_photos) {
        is_empty_deleted_photos = false;
        deleted_photos_list.push({'id': deleted_photo.value});
    }
    if (! is_empty_deleted_photos) {
        form_data.append('deleted_photos_set', JSON.stringify(deleted_photos_list));
    }
    if (category && ! isNaN(Number(category.value))) {
        form_data.append('category', category.value);
    }
    if (subcategory && ! isNaN(Number(subcategory.value))) {
        form_data.append('subcategory', subcategory.value);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/' + album_id + '/update/';

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
        console.log(result);

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/albums/show/' + result.slug);
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

            if (result.photos_set) {
                photos[0].insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.photos_set}</div>`);
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

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}