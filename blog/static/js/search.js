var form_search = document.querySelector('#form_search');

if (form_search) {
    form_search.addEventListener('submit', send_search);
}

async function send_search(e) {
    e.preventDefault();
    var search = document.querySelector('input[name="search"]');
    var url = window.location.protocol + '//' + window.location.host + '/search/' + search.value + '/';
    window.location.replace(url);
}