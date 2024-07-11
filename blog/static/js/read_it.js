function _getCookie(name) {
    let cookieArr = document.cookie.split("; ");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0]) {
            return cookiePair[1];
        }
    }
    return null;
}

var _read_it = document.querySelector('#read_it');

var _csrftoken = _getCookie('csrftoken');

_read_it.addEventListener('click', send_read_it);

async function send_read_it(e) {
    e.preventDefault();

    url = window.location.protocol + '//' + window.location.host + '/api/v1/notifications/read-it/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': _csrftoken,
        },
    });

    if (response.ok) {
        var result = await response.json();
        
        if (result.success) {
            document.querySelector('#notifications').innerHTML = '<p style="padding: 30px; text-align: center;">No new notifications</p>';
            document.querySelector('#read_it').disabled = true;
        }
    } else {
        alert('Backend error');
    }
}

var read_it_disabled = document.querySelector('.disabled_read');
if (read_it_disabled) {
    read_it_disabled.disabled = true;
}