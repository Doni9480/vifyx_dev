let btn = document.querySelector('.btn_input');
let tags = document.querySelector('#tags');
let block_tags = document.querySelector('#block_tags');

btn.disabled = true;

tags.addEventListener('input', function() {
    if (! tags.value) {
        btn.disabled = true;
    } else {
        btn.disabled = false;
    }
});

tags_list = [];
btn.addEventListener('click', function() {
    if (tags.value && !(tags_list.includes(tags.value))) {
        tags_list.push(tags.value);
        
        let fix_tags_value = tags.value.replace(/\s/g, "_");

        let element = document.createElement('input');
        element.name = 'tags';
        element.type = 'hidden';
        element.id = 'input_' + fix_tags_value;
        element.value = tags.value;
        block_tags.insertAdjacentElement('afterbegin', element);

        let selected_tags = document.querySelector('#selected_tags');
        let url = window.location.protocol + '//' + window.location.host + '/static/images/cross-svgrepo-com.svg';

        let tag = `<div class="tag" id="div_${fix_tags_value}" style="margin-bottom: 5px;">
            <span class="tag-text" id="tags.value">${tags.value}</span>
		    <img class="img-delete" onclick="delete_tag('${tags.value}')" src="${url}" width="10" height="10" style="margin-top: -1px; cursor: pointer;">
	    </div>`;

        selected_tags.innerHTML += tag + ' ';
        tags.value = '';
        btn.disabled = true;
    }
});

let svgs = document.querySelectorAll('#img-delete');

function delete_tag(tag_value) {
    let fix_tag_value = tag_value.replace(/\s/g, "_");
    let div_tag = document.querySelector(`#div_${fix_tag_value}`);
    let input_tag = document.querySelector(`#input_${fix_tag_value}`);
    input_tag.remove();
    div_tag.remove();
    tags_list.splice(tag_value);
}