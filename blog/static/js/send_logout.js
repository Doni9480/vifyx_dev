let logout = document.querySelector('#logout');

if (logout) {
    logout.addEventListener('click', logout_send);
}


async function logout_send(e) {
    e.preventDefault();

    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/logout/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        let result = await response.json();
        console.log(result);

        if (result.response) {
            document.cookie =`blog_access_token=;max-age=0;path=/`;

            window.location.replace(window.location.protocol + '//' + window.location.host + '/registration/login/');
        }
    } else {
        alert('Backend error');
    }
}