var select_category = document.querySelector('#select_category');
var select_subcategories = document.querySelectorAll('#select_subcategory');
var reset_category = document.querySelector('#reset_category');
var namespace = document.querySelector('input[name="category_namespace"]')?.value;
var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

if (select_category) {
    select_category.addEventListener('change', send_select_category);
}

if (reset_category) {
    reset_category.addEventListener('click', send_reset_category);
}

if (select_subcategories) {
    select_subcategories.forEach(select_subcategory => {
        select_subcategory.addEventListener('change', send_select_subcategory);
    });
}

async function send_select_category(e) {
    e.preventDefault();

    if (select_category && ! isNaN(Number(select_category.value))) {
        url = window.location.protocol + '//' + window.location.host + `/api/v1/users/select_category_${namespace}/` + select_category.value + '/';

        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        });

        if (response.ok) {
            window.location.reload();
        }
    }
}

async function send_select_subcategory(e) {
    e.preventDefault();

    var deleted_select_subcategory = e.target.parentElement.querySelector('input[name="deleted_select_subcategory"]')?.value;
    if (! deleted_select_subcategory) {
        deleted_select_subcategory = 0;
    }

    console.log(deleted_select_subcategory);

    if (e.target && ! isNaN(Number(e.target.value))) {
        url = window.location.protocol + '//' + window.location.host + `/api/v1/users/select_subcategory_${namespace}/` + e.target.value + '/' + deleted_select_subcategory + '/';

        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
        });

        if (response.ok) {
            window.location.reload();
        }
    }
}

async function send_reset_category(e) {
    e.preventDefault();

    url = window.location.protocol + '//' + window.location.host + `/api/v1/users/destroy_category_${namespace}/`

    var response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        window.location.reload();
    }
}