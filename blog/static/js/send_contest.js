document.querySelector('#form_contest').addEventListener('submit', function(e) {
    e.preventDefault();
});

document.querySelector('#id_publish').addEventListener('click', send_contest);

async function send_contest() {
    var preview = document.querySelector('input[name="preview"]');
    var title = document.querySelector('input[name="title"]');
    var description = document.querySelector('#id_description');
    var start_date = document.querySelector('input[name="start_date"]');
    var end_date = document.querySelector('input[name="end_date"]');
    var language = document.querySelector('#id_language');
    var item_type = document.querySelector('#id_item_type');
    var criteries = document.querySelector('#id_criteries');

    var form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    form_data.append('title', title.value);
    form_data.append('description', description.value);
    form_data.append('start_date', start_date.value);
    form_data.append('end_date', end_date.value);
    if (language.value == 'russian' || language.value == 'english') {
        form_data.append('language', language.value);   
    }
    if (item_type.value == 'post' || item_type.value == 'album' || item_type.value == 'quest') {
        form_data.append('item_type', item_type.value);
    }
    if (criteries.value == 'likes' || criteries.value == 'views' || criteries.value == 'assessment') {
        form_data.append('criteries', criteries.value);
    }
    
    url = window.location.protocol + '//' + window.location.host + '/api/v1/contests/create/';

    csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        var result = await response.json();
        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/contests/show/' + result.slug + '/');
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

            if (result.start_date) {
                start_date.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.start_date}</div>`);
            }

            if (result.end_date) {
                end_date.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.end_date}</div>`);
            }

            if (result.language) {
                language.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.language}</div>`);
            }

            if (result.item_type) {
                item_type.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.item_type}</div>`);
            }

            if (result.criteries) {
                criteries.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.criteries}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}