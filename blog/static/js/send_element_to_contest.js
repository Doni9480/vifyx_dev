document.querySelector('#form_element')?.addEventListener('submit', function(e) {
    e.preventDefault();
});

document.querySelector('#id_add')?.addEventListener('click', add_element);

async function add_element(e) {
    e.preventDefault();

    var element = document.querySelector('#id_element');
    var contest = document.querySelector('input[name="contest"]')?.value;

    var form_data = new FormData();
    if (element.value) {
        form_data.append('id', element.value);
    }

    url = window.location.protocol + '//' + window.location.host + '/api/v1/contests/add_element/' + contest + '/';

    csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    if (response.ok) {
        var result = await response.json();
        if (result.success) {
            window.location.reload();
        } else {
            if (result.id) {
                element.insertAdjacentHTML('beforebegin', `<div id="form-error" style="color: red;">${result.id}</div>`);
            }
        }
    } else {
        alert('Backend error');
    }
}