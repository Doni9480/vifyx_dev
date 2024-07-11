const questions = [
    // {
    //     question: "Какой язык используется для веб-разработки?",
    //     options: ["Python", "JavaScript", "C++", "Java"],
    //     correct: 1
    // },
    // {
    //     question: "AКакой язык используется для веб-разработки?",
    //     options: ["Python", "JavaScript", "C++", "Java"],
    //     correct: 1
    // },
    // {
    //     question: "BКакой язык используется для веб-разработки?",
    //     options: ["Python", "JavaScript", "C++", "Java"],
    //     correct: 1
    // },
    // {
    //     question: "CКакой язык используется для веб-разработки?",
    //     options: ["Python", "JavaScript", "C++", "Java"],
    //     correct: 1
    // },
    // можно добавить больше вопросов
];

async function load_tests() {
    let test_id = document.querySelector('input[name="test_id"]')?.value;
    let post_id = document.querySelector('input[name="post_id"]')?.value;
    console.log(post_id);

    if (test_id) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/tests/' + test_id + '/';
    } else if (post_id) {
        url = window.location.protocol + '//' + window.location.host + '/api/v1/posts/test_run/' + post_id + '/';
    }
    let response = await fetch(url, {
        method: 'GET',
    })
    var result = await response.json()
    if (result){
        console.log(result.data);
        result.data.question_set.forEach(function(item){
            console.log(item);
            let answers = []
            let current_index = 0;
            item.answers_set.forEach(function(answer, ix){
                if (answer.is_true){
                    current_index = ix;
                }
                answers.push(answer.variant);
            });
            questions.push({
                question: item.question,
                options: answers,
                correct: current_index,
            });
        });
        // console.log(questions);
        await loadQuestion();
    }
}


let currentQuestionIndex = 0;
let score = 0;

document.addEventListener('DOMContentLoaded', async () => {
    await load_tests();
    

    document.getElementById('next-button').addEventListener('click', async () => {
        const selectedOption = document.querySelector('input[name="option"]:checked');
        if (selectedOption) {
            const answer = parseInt(selectedOption.value);
            if (answer === questions[currentQuestionIndex].correct) {
                score++;
            }
            currentQuestionIndex++;
            if (currentQuestionIndex < questions.length) {
                await loadQuestion();
            } else {
                await showResult();
            }
        }
    });

    document.getElementById('restart-button').addEventListener('click', async () => {
        currentQuestionIndex = 0;
        score = 0;
        await loadQuestion();
    });
});

async function loadQuestion() {
    const questionContainer = document.getElementById('question-container');
    questionContainer.innerHTML = '';

    const question = document.createElement('h3');
    question.textContent = questions[currentQuestionIndex]?.question;
    questionContainer.appendChild(question);

    questions[currentQuestionIndex].options.forEach((option, index) => {
        const label = document.createElement('label');
        label.innerHTML = `
            <input type="radio" name="option" value="${index}">
            ${option}
        `;
        questionContainer.appendChild(label);
        questionContainer.appendChild(document.createElement('br'));
    });
}

async function showResult() {
    const questionContainer = document.getElementById('question-container');
    questionContainer.innerHTML = `
        <h3>Ваш результат: ${score} из ${questions.length}</h3>
    `;
}