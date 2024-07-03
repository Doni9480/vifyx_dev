let form_delete = document.querySelector('#form_delete');

if (form_delete) {
    form_delete.addEventListener('submit', delete_survey);
}


async function delete_survey(e) {
    e.preventDefault();

    let survey_id = document.querySelector('input[name="survey_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/surveys/' + survey_id + '/delete/';

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