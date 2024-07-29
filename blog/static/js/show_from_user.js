var shows_from_user = document.querySelectorAll('#button_show');

shows_from_user.forEach(show_from_user => {
    show_from_user.addEventListener('click', send_show_from_user);
});

async function send_show_from_user(e) {
    e.preventDefault();

    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var url = window.location.protocol + '//' + window.location.host + '/api/v1/users/' + e.target.value + '/show_from_user/';

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