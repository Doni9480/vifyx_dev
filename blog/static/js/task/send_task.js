document.querySelector('#form_post').addEventListener('submit', function(e) {
    e.preventDefault();
});

// document.querySelector('#id_publish').addEventListener('click', send_post);
document.querySelector('#id_save').addEventListener('click', send_post);

async function send_post() {
    let task_type = document.querySelector('select[name="task_type"]');
    let content_usage_type = document.querySelector('select[name="content_usage_type"]');
    let name = document.querySelector('input[name="name"]');
    let description = document.querySelector('textarea[name="description"]');
    let points_reward = document.querySelector('input[name="points_reward"]');
    let deadline = document.querySelector('input[name="deadline"]');
    let total_pool_points = document.querySelector('input[name="total_pool_points"]');
    let external_link = document.querySelector('input[name="external_link"]');

    let redirect_url = document.querySelector('input[name="redirect_url"]');
    let campaign_pk = document.querySelector('input[name="campaign_pk"]');

    let csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let g_recaptcha_response = document.querySelector('input[name="g_recaptcha_response"]');

    let form_data = new FormData();
    if (task_type) {
        form_data.append('task_type', task_type.value);
    }
    if (name) {
        form_data.append('name', name.value);
    }
    if (content_usage_type) {
        form_data.append('content_usage_type', content_usage_type.value);
    }
    if (description) {
        form_data.append('description', description.value);
    }
    if (points_reward) {
        form_data.append('points_reward', points_reward.value);
    }
    if (deadline) {
        form_data.append('deadline', deadline.value);
    }
    if (total_pool_points) {
        form_data.append('total_pool_points', total_pool_points.value);
    }
    if (external_link) {
        form_data.append('external_link', external_link.value);
    }
    if (campaign_pk) {
        form_data.append('campaign', campaign_pk.value);
    }
    
    form_data.append('g_recaptcha_response', g_recaptcha_response.value);

    url = window.location.protocol + '//' + window.location.host + '/api/v1/companies/tasks/create/';

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
            window.location.replace(redirect_url.value);
        } else {
            form_errors = document.querySelectorAll('#form-error');

            for (const form_error of form_errors) {
                form_error.remove();
            }

            if (result.recaptcha) {
                form_post.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.recaptcha}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}


