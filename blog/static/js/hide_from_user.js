var hides_from_user = document.querySelectorAll('#button_hide');

hides_from_user.forEach(hide_from_user => {
    hide_from_user.addEventListener('click', send_hide_from_user);
});

async function send_hide_from_user(e) {
    e.preventDefault();

    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var url = window.location.protocol + '//' + window.location.host + '/api/v1/users/' + e.target.value + '/hide_from_user/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        var result = await response.json();
        if (result.success) {
            window.location.reload();
        }
    }
}