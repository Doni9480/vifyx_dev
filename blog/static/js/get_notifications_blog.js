var get_notifications_blog = document.querySelector('input[name="get_notifications_blog"]');

if (get_notifications_blog) {
    get_notifications_blog.addEventListener('change', send_notifications_blog);
}

var blog_id = document.querySelector('input[name="blog_id"]')?.value;

async function send_notifications_blog(e) {
    e.preventDefault();

    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

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