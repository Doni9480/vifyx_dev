let form_delete = document.querySelector('#form_delete');

if (form_delete) {
    form_delete.addEventListener('submit', delete_post);
}


async function delete_post(e) {
    e.preventDefault();

    let post_id = document.querySelector('input[name="post_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/' + post_id + '/delete/';

    let response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/my/profile/');
        }
    } else {
        alert('Backend error');
    }
}