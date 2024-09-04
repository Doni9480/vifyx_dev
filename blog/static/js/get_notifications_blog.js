document.querySelector('input[name="get_notifications_blog"]')?.addEventListener('change', send_notifications_blog);
document.querySelector('input[name="get_notifications_post"]')?.addEventListener('change', send_notifications_element);
document.querySelector('input[name="get_notifications_quest"]')?.addEventListener('change', send_notifications_element);
document.querySelector('input[name="get_notifications_album"]')?.addEventListener('change', send_notifications_element);
document.querySelector('input[name="get_notifications_answer"]')?.addEventListener('change', send_notifications_element);
csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

var blog_id = document.querySelector('input[name="blog_id"]')?.value;

async function send_notifications_blog(e) {
    e.preventDefault();

    var form_data = new FormData();
    if (e.target.checked) {
        form_data.append('get_notifications_blog', 1);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/notifications/' + blog_id + '/get_notifications_blog/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });
}

async function send_notifications_element(e) {
    e.preventDefault();

    if (e.target.name == 'get_notifications_post') {
        namespace = 'posts';
    }
    if (e.target.name == 'get_notifications_quest') {
        namespace = 'quests';
    }
    if (e.target.name == 'get_notifications_album') {
        namespace = 'albums';
    }
    if (e.target.name == 'get_notifications_answer') {
        namespace = 'answers';
    }

    var form_data = new FormData();
    if (e.target.checked) {
        form_data.append('get_notifications_element', 1);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/notifications/' + blog_id + '/get_notifications/' + namespace + '/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data,
    });
}