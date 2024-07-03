let question_form = document.querySelector('#form_question');



question_form.addEventListener('submit', function(e) {
    e.preventDefault();
});

question_form.querySelector('#id_save').addEventListener('click', async () => {
    
    let question_answers = document.querySelectorAll('.questions__item');

    let qid = await add_question();
    if (qid){
        question_answers.forEach(async function(item) {
            let answer_text = item.querySelector('#add_question_text').value;
            let is_true = item.querySelector('input[name="is_true"]').checked === true;
            if (answer_text){
                console.log(answer_text, is_true);
                await add_question_answer(qid, answer_text, is_true);
            }
        });
    }
});


async function add_question() {
    let csrftoken = question_form.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');
    let test_slug = document.querySelector('#test_url-link');
    let preview = question_form.querySelector('input[name="preview"]');
    let question_text = document.querySelector('#id_question');
    let quest_id = document.querySelector('#quest_id');

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('preview', preview.files[0]);
    }
    if (question_text) {
        form_data.append('question', question_text.value);
    }
    if (quest_id) {
        form_data.append('quest', quest_id.value);
    }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/quest/' + quest_id.value + '/question_cerate/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    
    get_g_token();

    if (response.ok) {
        let result = await response.json();
        
        form_errors = document.querySelectorAll('#form-error');
        
        for (const form_error of form_errors) {
            form_error.remove();
        }
        
        if (result.success) {
            return result.data.id;
            // window.location.replace(window.location.protocol + '//' + window.location.host + '/test/');
        } else if (result.ban) {
            window.scrollTo(0, 0);
            
            form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        } else {
            if (result.preview) {
                preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            }

            // if (result.title) {
            //     title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            // }

            if (result.question_text) {
                question_text.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.question_text}</div>`);
            }

            // if (result.content) {
            //     content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            // }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
            return result.data.id
        }
    } else {
        alert('Backend error');
        return null;
    }
    


}

async function add_question_answer(question_id, answer_text, is_true) {
    console.log(question_id);
    let csrftoken = question_form.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]').value;
    let test_slug = document.querySelector('#test_url-link');

    get_g_token();

    let form_data = new FormData();
    form_data.append('is_true', is_true);
    form_data.append('variant', answer_text);
    form_data.append('question', question_id);
    form_data.append('g_recaptcha_response', g_recaptcha_response);


    url = window.location.protocol + '//' + window.location.host + '/api/v1/quest/question_answer_cerate/' + question_id + '/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        let result = await response.json();
        
        form_errors = document.querySelectorAll('#form-error');
        
        for (const form_error of form_errors) {
            form_error.remove();
        }
        
        if (result.success) {
            window.location.replace(window.location.protocol + '//' + window.location.host + test_slug);
        } else if (result.ban) {
            window.scrollTo(0, 0);
            
            form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
        } else {
            // if (result.preview) {
            //     preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            // }

            // if (result.title) {
            //     title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            // }

            // if (result.question_text) {
            //     question_text.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.description}</div>`);
            // }

            // if (result.content) {
            //     content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
            // }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
            // return result.data.id
        }
    } else {
        alert('Backend error');
        return null;
    }
    window.location.replace(window.location.protocol + '//' + window.location.host + test_slug);
}

// async function send_draft() {
//     let preview = document.querySelector('input[name="preview"]');
//     let title = document.querySelector('input[name="title"]');
//     let description = document.querySelector('#id_description');
//     let content = document.querySelector('#id_content');
//     let tags = document.querySelectorAll('input[name="tags"]');
//     let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

//     tags_list = [];
//     tags.forEach(tag => {
//         tags_list.push(tag.value);
//     });

//     let form_data = new FormData();
//     if (preview.files[0]) {
//         form_data.append('preview', preview.files[0]);
//     }
//     if (title) {
//         form_data.append('title', title.value);
//     }
//     if (description) {
//         form_data.append('description', description.value);
//     }
//     if (content) {
//         form_data.append('content', content.value);
//     }
//     if (tags_list) {
//         form_data.append('tags', tags_list);
//     }
//     form_data.append('g_recaptcha_response', g_recaptcha_response.value);

//     url = window.location.protocol + '//' + window.location.host + '/api/v1/test/create/';

//     let response = await fetch(url, {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': csrftoken,
//         },
//         body: form_data
//     });

    
//     get_g_token();

//     if (response.ok) {
//         let result = await response.json();

//         if (result.success) {
//             form_successes = document.querySelectorAll('#form-success');

//             for (const form_success of form_successes) {
//                 form_success.remove();
//             }

//             document.querySelector('#id_save').insertAdjacentHTML('beforebegin', `<div id="form-success" style="color: green;">Successfully saved!</div>`);
//         } else {
//             form_errors = document.querySelectorAll('#form-error');

//             for (const form_error of form_errors) {
//                 form_error.remove();
//             }

//             if (result.recaptcha) {
//                 form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
//             }
//         }
//     } else {
//         alert('Backend error');
//     }
// }


// async function send_post(e) {
//     e.preventDefault();

//     let preview = document.querySelector('input[name="preview"');
//     let title = document.querySelector('input[name="title"]');
//     let description = document.querySelector('#id_description');
//     let content = document.querySelector('#id_content');
//     let tags = document.querySelectorAll('input[name="tags"]');
//     let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
//     let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

//     tags_list = [];
//     tags.forEach(tag => {
//         tags_list.push(tag.value);
//     });

//     let form_data = new FormData();
//     if (preview.files[0]) {
//         form_data.append('preview', preview.files[0]);
//     }
//     form_data.append('title', title.value);
//     form_data.append('description', description.value);
//     form_data.append('content', content.value)
//     form_data.append('tags', tags_list);
//     form_data.append('g_recaptcha_response', g_recaptcha_response.value);

//     url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/create';

//     let response = await fetch(url, {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': csrftoken,
//         },
//         body: form_data
//     });

//     get_g_token();

//     if (response.ok) {
//         let result = await response.json();

//         form_errors = document.querySelectorAll('#form-error');

//         for (const form_error of form_errors) {
//             form_error.remove();
//         }

//         if (result.success) {
//             window.location.replace(window.location.protocol + '//' + window.location.host + '/posts/show/' + result.slug);
//         } else if (result.ban) {
//             window.scrollTo(0, 0);
            
//             form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.ban}</div>`);
//         } else {
//             if (result.preview) {
//                 preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
//             }

//             if (result.title) {
//                 title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
//             }

//             if (result.description) {
//                 description.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.description}</div>`);
//             }

//             if (result.content) {
//                 content.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.content}</div>`);
//             }

//             if (result.recaptcha) {
//                 form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
//             }
//         }
//     } else {
//         alert('Backend error');
//     }
// }
