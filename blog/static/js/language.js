var language = document.querySelector('#language');

language.addEventListener('change', set_language);

async function set_language(e) {
    e.preventDefault();

    var radios = document.querySelectorAll('input[name="radio-group-2"]');
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    var language = null;
    radios.forEach(radio => {
        if (radio.checked) {
            language = radio.value;
        }
    });

    if (language && typeof language === 'string') {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/users/set_language/';

        var obj = {};
        obj.language = language;        
        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(obj),
        });
    }
}