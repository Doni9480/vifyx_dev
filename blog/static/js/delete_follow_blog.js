var delete_follow = document.querySelector('#delete_follow');

if (delete_follow) {
    delete_follow.addEventListener('click', delete_follow_blog);
}

async function delete_follow_blog(e) {
    e.preventDefault();

    var blog_id = document.querySelector('input[name="blog_id"]').value;
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    url = window.location.protocol + '//' + window.location.host + '/api/v1/blogs/delete_follow/' + blog_id + '/';
    
    var response = await fetch(url, {
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