let blog_id = document.querySelector('input[name="blog_id"]')?.value;

let follow = document.querySelector('#follow');
if (follow) {
    follow.addEventListener('click', send_follow);
}

async function send_follow(e) {
    e.preventDefault();

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/' + blog_id + '/follow/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"').value,
        },
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    }
}

let unfollow = document.querySelector('#unfollow');
if (unfollow) {
    unfollow.addEventListener('click', send_unfollow);
}

async function send_unfollow(e) {
    e.preventDefault();

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/' + blog_id + '/unfollow/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"').value,
        },
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            window.location.reload();
        }
    } else {
        alert('Backend error');
    } 
}