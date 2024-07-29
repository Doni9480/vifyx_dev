let form_delete = document.querySelector('#form_delete');

if (form_delete) {
    form_delete.addEventListener('submit', delete_quest);
}


async function delete_quest(e) {
    e.preventDefault();

    let quest_id = document.querySelector('input[name="quest_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/' + quest_id + '/delete/';

    let response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        window.location.replace(window.location.protocol + '//' + window.location.host + '/my/profile/');
    } else {
        alert('Backend error');
    }
}