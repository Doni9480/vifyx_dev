let form_question = document.querySelector('#form_question');

form_question.addEventListener('submit', form_prevent_default);

async function form_prevent_default(e) {
    e.preventDefault();
}

let save_btn = document.getElementById('id_save');
save_btn.addEventListener('click', edit_question);
async function edit_question (e) {
    e.preventDefault();
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    
    let question_text = document.querySelector('textarea[name="question"]').value;
    let test_slug = document.querySelector('input[name="test_slug"]')?.value;
    let quest_slug = document.querySelector('input[name="quest_slug"]')?.value;
    let post_slug = document.querySelector('input[name="post_slug"]')?.value;
    let question_id = document.querySelector('input[name="id_question"]').value;
    let question_answers = document.querySelectorAll('.questions__item')
    let answers_list = [];
    question_answers.forEach(function (item) {
        let answer_text = item.querySelector('input[name="variant"]').value;
        let answer_is_true = item.querySelector('input[name="is_true"]').checked;
        let answer_id = item.querySelector('input[name="answer_id"]').value;

        answers_list.push({
            variant: answer_text,
            is_true: answer_is_true,
            id: answer_id
        });
    });

    let data = {
        question: question_text,
        answers_set: answers_list,
        g_recaptcha_response: g_recaptcha_response
    }

    if (test_slug) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/question/' + question_id + '/update/';
    } else if (quest_slug) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/question/' + question_id + '/edit/';
    } else if (post_slug) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/question/' + question_id + '/update/';
    }

    let config = {
        headers: {
            'X-CSRFToken': csrftoken,
        }
    }
    axios.patch(url, data, config)
    .then(function(r) {
        if (r.data.success) {
            alert('saved successfully');
            if (test_slug) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/tests/' + test_slug);
            } else if (quest_slug) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/quests/' + quest_slug);
            } else if (post_slug) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/posts/show/' + post_slug);
            }
        } else {
            alert(r.data.error);
        }
    }).catch(function(r) {
        console.log(r);
        if (r.response.status == 400) {
            if (r.response.data.data.answers_set) {
                r.response.data.data.answers_set.forEach(err => {
                    if (err.variant) {
                        alert('Answer option: ' + err.variant);
                    }
                });
            } 
            if (r.response.data.data.question) {
                alert('Question: ' + r.response.data.data.question);
            }
        } else { 
            alert('Backend error');
        }
    }).finally(function() {
        get_g_token();
    });
}