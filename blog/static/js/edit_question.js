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
    let quest_slug = document.querySelector('input[name="quest_slug"]')?.value;
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

    let form_data = new FormData();
    form_data.append('question', question_text);
    form_data.append('answers_set', JSON.stringify(answers_list));
    form_data.append('g_recaptcha_response', g_recaptcha_response);

    if (test_slug) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/test/question_edit/' + question_id + '/';
    } else {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/question/' + question_id + '/edit/';
    }

    let response = await fetch(url, {
        method: 'PATCH',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    })

    get_g_token();

    if (response.ok) {
        let result = await response.json();
        if (result.success) {
            alert('saved successfully');
            if (test_slug) {
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