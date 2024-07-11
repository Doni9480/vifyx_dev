var buy_button = document.querySelector('#buy_button');

if (buy_button) {
    buy_button.addEventListener('click', buy);
}

async function buy(e) {
    e.preventDefault();

    var post_id = document.querySelector('input[name="post_id"]').value;

    var url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/buy/' + post_id + '/';

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        var result = await response.json();

        if (result.success) {
            window.location.reload();
        } else {
            if (result.error_scores) {
                buy_button.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.error_scores}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}