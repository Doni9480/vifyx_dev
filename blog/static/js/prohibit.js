let prohibit_comment = document.querySelector('#prohibit_comment');
let prohibit_post = document.querySelector('#prohibit_post');
let allow_comment = document.querySelector('#allow_comment');
let allow_post = document.querySelector('#allow_post');

if (prohibit_comment) {
    prohibit_comment.addEventListener('click', send_prohibit_comment);
}
if (prohibit_post) {
    prohibit_post.addEventListener('click', send_prohibit_post);
}
if (allow_comment) {
    allow_comment.addEventListener('click', send_allow_comment);
}
if (allow_post) {
    allow_post.addEventListener('click', send_allow_post);
}


async function send_prohibit_comment(e) {
    e.preventDefault();

    let user_id = document.querySelector('input[name="user_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/forbid_to_comment/' + user_id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}

async function send_prohibit_post(e) {
    e.preventDefault();

    let user_id = document.querySelector('input[name="user_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/forbid_to_post/' + user_id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}

async function send_allow_comment(e) {
    e.preventDefault();

    let user_id = document.querySelector('input[name="user_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/allow_to_comment/' + user_id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}

async function send_allow_post(e) {
    e.preventDefault();

    let user_id = document.querySelector('input[name="user_id"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/users/allow_to_post/' + user_id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    });

    get_g_token();

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}