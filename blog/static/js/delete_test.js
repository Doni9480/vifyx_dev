let form_delete = document.querySelector('#form_delete');

if (form_delete) {
    form_delete.addEventListener('submit', delete_post);
}


async function delete_post(e) {
    e.preventDefault();

    let test_id = document.querySelector('input[name="test_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    url = window.location.protocol + '//' + window.location.host + '/api/v1/test/delete/' + test_id + '/';

    let response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        
    });

    if (response.ok) {
            window.location.replace(window.location.protocol + '//' + window.location.host + '/test/');
    } else {
        alert('Backend error');
    }
}