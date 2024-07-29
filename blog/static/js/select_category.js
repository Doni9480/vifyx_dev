var select_category = document.querySelector('#select_category');
var select_subcategory = document.querySelector('#select_subcategory');

if (select_category) {
    select_category.addEventListener('change', function() {
        if (select_category && ! isNaN(Number(select_category.value))) {
            window.location.replace(window.location.protocol + '//' + window.location.host + window.location.pathname + '?category=' + select_category.value);
        }
    });
}

if (select_subcategory) {
    select_subcategory.addEventListener('change', function() {
        if (select_subcategory && ! isNaN(Number(select_subcategory.value))) {
            var url = new URL(window.location.href);
            var category = url.searchParams.get("category");
            window.location.replace(window.location.protocol + '//' + window.location.host + window.location.pathname + '?category=' + category + '&subcategory=' + select_subcategory.value);
        }
    });
}