var btns = document.querySelectorAll('#username_unfollow');

if (btns) {
    btns.forEach(btn => {
        btn.addEventListener('click', send_unfollow);
    });
}

async function send_unfollow(e) {
    e.preventDefault();

    var username = e.target.value;
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/unfollow/' + username + '/';

    var response = await fetch(url, {
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
    } else {
        alert('Backend error');
    }
}