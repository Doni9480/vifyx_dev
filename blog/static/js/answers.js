let add_more = document.querySelector('#add_more');

let num_answers = document.querySelector('#num_answers');

let answers = document.querySelectorAll('#answer');
num_answers.innerHTML = 10 - answers.length;

add_more.addEventListener('click', function() {
    let answers = document.querySelectorAll('#answer');

    if (answers.length <= 10) {
        document.querySelector('#answers_block').insertAdjacentHTML(
            'beforeend',
            `
                <div class="col-12 form-group d-flex" id="answer">
                    <input type="text" class="form-control" name="answers">
                    <button type="button" class="btn btn-danger btn_remove" onclick="remove_answer(this)">Remove</button>
                </div>
            `
        );

        num_answers.innerHTML = 10 - (answers.length + 1);
    }

    if ((answers.length + 1) >= 10) {
        add_more.disabled = true;
    }
});

function remove_answer(e) {
    let answers = document.querySelectorAll('#answer');

    if (answers.length >= 2) {
        e.parentNode.remove();

        num_answers.innerHTML = 10 - (answers.length - 1);
    }
}