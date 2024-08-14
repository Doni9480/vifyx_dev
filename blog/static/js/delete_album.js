let form_delete = document.querySelector('#form_delete');

if (form_delete) {
    form_delete.addEventListener('submit', delete_album);
}


async function delete_album(e) {
    e.preventDefault();

    let album_id = document.querySelector('input[name="album_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/albums/' + album_id + '/delete/';

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