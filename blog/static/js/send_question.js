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
        url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/question/cerate/';
    } else {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/' + quest_id + '/question/cerate/';
    }
    

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: data
    })

    get_g_token();

    if (response.ok) {
        let result = await response.json();
        if (result.success) {
            alert('saved successfully');
            if (test_id) {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/test/' + test_slug);
            } else {
                window.location.replace(window.location.protocol + '//' + window.location.host + '/quest/' + quest_slug);
            }
        } else {
            alert(result.error);
        }
    } else {
        let result = await response.json();
        alert(result.error);
    }

}