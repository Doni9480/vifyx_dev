let form_comment = document.querySelector('#commentform');
if (form_comment) {
    form_comment.addEventListener('submit', send_comment);
}

let form_answers = document.querySelectorAll('#answerform');
form_answers.forEach(form_answer => {
    form_answer.addEventListener('submit', function(e) {
        e.preventDefault();

        send_answer(form_answer);
    });
});

function form_reply(id) {
    let comment = document.querySelector(`#comment_${id}`);
    comment.querySelector('form').style.display = 'block';
}

async function send_comment(e) {
    e.preventDefault();
    let survey_id = document.querySelector('input[name="survey_id"]');
    let post_id = document.querySelector('input[name="post_id"]');
    let test_id = document.querySelector('input[name="test_id"]');
    let quest_id = document.querySelector('input[name="quest_id"]');
    let album_id = document.querySelector('input[name="album_id"]');

    let comment_text = document.querySelector('#id_comment');
    if (survey_id) {
        let survey_id = document.querySelector('input[name="survey_id"]');
    } else if (post_id) {
        let post_id = document.querySelector('input[name="post_id"]');
    } else if (test_id) {
        let test_id = document.querySelector('input[name="test_id"]');
    } else if (quest_id) {
        let quest_id = document.querySelector('input[name="quest_id"]');
    } else if (album_id) {
        let album_id = document.querySelector('input[name="album_id"]');
    }

    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    let form_data = new FormData();
    form_data.append('text', comment_text.value);
    form_data.append('timezone', timezone);

    if (survey_id) {
        form_data.append('survey', Number(survey_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/create/survey/';
    } else if (post_id) {
        form_data.append('post', Number(post_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/create/post/';
    } else if (test_id) {
        form_data.append('test', Number(test_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/create/test/';
    } else if (quest_id) {
        form_data.append('quest', Number(quest_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/create/quest/';
    } else if (album_id) {
        form_data.append('album', Number(album_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/create/album/';
    }

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            comment_text.value = '';

            html = delete_comment_block(result.id, result.username, result.text, result.date);
    
            document.querySelector('.commentlist').insertAdjacentHTML('beforeend', html);

            let form_answers = document.querySelectorAll('#answerform');
            form_answers.forEach(form_answer => {
                form_answer.addEventListener('submit', function(e) {
                    e.preventDefault();

                    send_answer(form_answer);
                });
            });
        } else if (result.ban) {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            form_comment.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        }
    } else {
        alert('Backend error');
    }
}

async function send_answer(form_answer) {
    console.log('ok');
    let answer_text = form_answer.querySelector('#id_answer');
    let comment_id = form_answer.querySelector('input[name="comment_id"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    let form_data = new FormData();
    form_data.append('text', answer_text.value);
    form_data.append('comment', Number(comment_id.value));
    form_data.append('timezone', timezone);

    let survey_id = document.querySelector('input[name="survey_id"]');
    let post_id = document.querySelector('input[name="post_id"]');
    let test_id = document.querySelector('input[name="test_id"]');
    let quest_id = document.querySelector('input[name="quest_id"]');
    let album_id = document.querySelector('input[name="album_id"]');

    if (survey_id) {
        form_data.append('survey', Number(survey_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/create/survey/';
    } else if (post_id) {
        form_data.append('post', Number(post_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/create/post/';
    } else if (test_id) {
        form_data.append('test', Number(test_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/create/test/';
    } else if (quest_id) {
        form_data.append('quest', Number(quest_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/create/quest/';
    } else if (album_id) {
        form_data.append('album', Number(album_id.value));
        url = window.location.protocol + '//' + window.location.host + '/api/v1/comments/answer/create/album/';
    }

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        let result = await response.json();

        if (result.success) {
            answer_text.value = '';

            let answers = document.querySelector(`#comment_${comment_id.value}`).querySelector('.children');
            let html = ` 
                <li id="answer_${result.id}" class="comment byuser comment-author-_smcl_admin odd alt depth-2" id="li-comment-3">
                
                    <div id="comment-3" class="comment-wrap">
    
                        <div class="comment-content d-flex justify-content-between align-items-start">
                            <div>
                                <div class="comment-author"><a href='/profile/${result.username}'
                                                                rel='external nofollow' class='url'>${result.username}</a><span>${result.date}</span>
                                </div>
    
                                <p>${result.text}</p>
                            </div>
    
                            <a style="cursor: pointer; color: var(--cnvs-themecolor);" onclick="delete_answer(${result.id})" id="${result.id}">delete</a>
                        </div>
    
                        <div class="clear"></div>
    
                    </div>
                </li>
            `;
    
            answers.insertAdjacentHTML('beforeend', html);
        } else if (result.ban) {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            form_answer.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        }


    } else {
        alert('Backend error');
    }
}