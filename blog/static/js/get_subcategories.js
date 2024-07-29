var category = document.querySelector('#id_category');
var namespace = document.querySelector('input[name="namespace"]');

category.addEventListener('change', get_subcategory);

async function get_subcategory(e) {
    e.preventDefault();

    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    url = window.location.protocol + '//' + window.location.host + '/api/v1/' + namespace.value + '/' + e.target.value + '/get_subcategory/';

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
    });

    if (response.ok) {
        var result = await response.json();
        var subcategories = result.subcategories;

        document.querySelector('#subcategories')?.remove();
        
        if (subcategories.length > 0) {
            var html_subcategories = ``;
            subcategories.forEach(subcategory => {
                html_subcategories += `<option value="${subcategory.id}">${subcategory.subcategory}</option>`
            });

            var html_text = `
                <div class="col-12 form-group" id="subcategories">
                    <label for="id_subcategory">Subcategory:</label>
                    <select id="id_subcategory" class="form-select">
                        <option disabled selected>Select a subcategory</option>
                        ${html_subcategories}
                    </select>
                </div>
            `;

            document.querySelector('#categories').insertAdjacentHTML('afterend', html_text);
        }
    }
}