
document.querySelector('#form_post').addEventListener('submit', function(e) {
    e.preventDefault();
});

// document.querySelector('#id_publish').addEventListener('click', send_post);
document.querySelector('#id_save').addEventListener('click', send_post);

async function send_post() {
    let preview = document.querySelector('input[name="image"]');
    let title = document.querySelector('input[name="name"]');
    let prize_fund = document.querySelector('input[name="prize_fund"]');
    let slug = document.querySelector('input[name="slug"]');
    let description = document.querySelector('#id_description');
    // let content = document.querySelector('#id_content');
    // let tags = document.querySelectorAll('input[name="tags"]');
    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    // tags_list = [];
    // tags.forEach(tag => {
    //     tags_list.push(tag.value);
    // });

    let form_data = new FormData();
    if (preview.files[0]) {
        form_data.append('image', preview.files[0]);
    }
    if (title) {
        form_data.append('name', title.value);
    }
    if (prize_fund) {
        form_data.append('prize_fund', prize_fund.value);
    }
    if (slug) {
        form_data.append('slug', slug.value);
    }
    if (description) {
        form_data.append('description', description.value);
    }
    // if (content) {
    //     form_data.append('content', content.value);
    // }
    // if (tags_list) {
    //     form_data.append('tags', tags_list);
    // }
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/companies/create/';

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

        if (result.success) {
            form_successes = document.querySelectorAll('#form-success');

            for (const form_success of form_successes) {
                form_success.remove();
            }

            
            document.querySelector('#id_save').insertAdjacentHTML('beforebegin', `<div id="form-success" style="color: green;">Successfully saved!</div>`);
            window.location.replace('/my/profile/');
        } else {
            form_errors = document.querySelectorAll('#form-error');

            // for (const form_error of form_errors) {
            //     form_error.remove();
            // }

            if (result.error.preview) {
                preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.preview}</div>`);
            }

            if (result.error.prize_fund) {
                prize_fund.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.error.prize_fund}</div>`);
            }

            // if (result.error.title) {
            //     title.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.title}</div>`);
            // }

            // if (result.description) {
            //     description.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.description}</div>`);
            // }

            // if (result.slug) {
            //     url_blog.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.slug}</div>`);
            // }

            // if (result.is_private) {
            //     is_private.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.is_private}</div>`);
            // }

            // if (result.recaptcha) {
            //     form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            // }
        }
    } else {
        let result = await response.json();
        
        if (result.error.image) {
            preview.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.error.image}</div>`);
        }

        if (result.error.prize_fund) {
            prize_fund.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.error.prize_fund}</div>`);
        }
        alert('Backend error');
    }
}


// async function send_post2(e) {
//     e.preventDefault();

//     let preview = document.querySelector('input[name="preview"');
//     let title = document.querySelector('input[name="title"]');
//     let description = document.querySelector('#id_description');
//     let content = document.querySelector('#id_content');
//     // let tags = document.querySelectorAll('input[name="tags"]');
//     let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"').value;
//     let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

//     // tags_list = [];
//     // tags.forEach(tag => {
//     //     tags_list.push(tag.value);
//     // });

//     let form_data = new FormData();
//     if (preview.files[0]) {
//         form_data.append('preview', preview.files[0]);
//     }
//     form_data.append('title', title.value);
//     form_data.append('description', description.value);
//     form_data.append('content', content.value)
//     // form_data.append('tags', tags_list);
//     form_data.append('g_recaptcha_response', g_recaptcha_response.value);

//     url = window.location.protocol + '//' + window.location.host + '/api/v1/quests/create';

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
