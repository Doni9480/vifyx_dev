let form_question = document.querySelector('#form_question');
form_question.addEventListener('submit', form_prevent_default);

async function form_prevent_default(e) {
    e.preventDefault();
}
let save_btn = document.getElementById('id_save');
save_btn.addEventListener('click', create_question);
async function create_question (e) {
    e.preventDefault();
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]').value;
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
    
    let question_text = document.querySelector('textarea[name="question"]').value;
    let test_slug = document.querySelector('input[name="test_slug"]')?.value;
    let test_id = document.querySelector('input[name="id_test"]')?.value;
    let post_slug = document.querySelector('input[name="post_slug"]')?.value;
    let post_id = document.querySelector('input[name="id_post"]')?.value;
    let quest_slug = document.querySelector('input[name="quest_slug"]')?.value;
    let quest_id = document.querySelector('input[name="id_quest"]')?.value;
    let question_answers = document.querySelectorAll('.questions__item')
    let answers_list = [];
    question_answers.forEach(function (item) {
        let answer_text = item.querySelector('input[name="variant"]').value;
        let answer_is_true = item.querySelector('input[name="is_true"]').checked;

        answers_list.push({
            variant: answer_text,
            is_true: answer_is_true
        });
    });
    let data = {
        question: question_text,
        answers_set: answers_list,
        g_recaptcha_response: g_recaptcha_response
    }

    if (test_id) {
        data = {
            ...data,
            test: test_id
        }
        url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/question/create/';
    } else if (quest_id) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/' + quest_id + '/question/create/';
    } else if (post_id) {
        data = {
            ...data,
            text: question_text,
            post: post_id
        }
        url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/question/create/';
    }
    
    let config = {
        headers: {
            'X-CSRFToken': csrftoken,
        }
    }
    axios.post(url, data, config)
    .then(function(r) {
        if (r.data.success) {
            alert('saved successfully');
            if (post_id) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/posts/show/' + post_slug);
            } else if (test_id) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/tests/' + test_slug);
            } else if (quest_id) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/quests/' + quest_slug);
            }
        } else {
            alert(r.data.error);
        }
    }).catch(function(r) {
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