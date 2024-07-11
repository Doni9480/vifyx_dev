function getCookie(name) {
    let cookieArr = document.cookie.split("; ");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0]) {
            return cookiePair[1];
        }
    }
    return null;
}

var form = document.querySelector('#delete_all_notifications');

if (form) {
    form.addEventListener('submit', send_delete);
}

async function send_delete(e) {
    e.preventDefault();

    let csrftoken = getCookie('csrftoken');

    url = window.location.protocol + '//' + window.location.host + '/api/v1/notifications/delete-all/';

    let response = await fetch(url, {
        method: 'DELETE',
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