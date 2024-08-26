let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;

async function delete_forever(id) {
    url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/delete/' + id + '/';

    let response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        result = await response.json();

        if (result.success) {
            document.querySelector(`#comment_${id}`).remove();
        }
    } else {
        alert('Backend error');
    }
}

async function delete_from_user(id) {
    url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/delete_from_user/' + id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        result = await response.json();

        if (result.success) {
            let comment = document.querySelector(`#comment_${result.id}`);
            comment = comment.querySelector('#comment-2');
            comment.innerHTML = delete_comment_block_user(result.id);

            let form_answers = document.querySelectorAll('#answerform');
            form_answers.forEach(form_answer => {
                form_answer.addEventListener('submit', function(e) {
                    e.preventDefault();

                    send_answer(form_answer);
                });
            });
        }
    } else {
        alert('Backend error');
    }
}

async function delete_answer(id) {
    url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/delete/' + id + '/';

    let response = await fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        result = await response.json();

        if (result.success) {
            document.querySelector(`#answer_${id}`).remove();
        }
    } else {
        alert('Backend error');
    }
}