var form_search_tags = document.querySelector('#form_search_tags');

if (form_search_tags) {
    form_search_tags.addEventListener('submit', send_search_tags);
}

async function send_search_tags(e) {
    e.preventDefault();
    var search_tags = document.querySelector('input[name="search_tags"]');
    var url = window.location.protocol + '//' + window.location.host + '/search_tags/' + search_tags.value + '/';
    window.location.replace(url);
}