const questionTime = document.getElementById('questionTime')
const time = questionTime.dataset.questionTime

questionTime.innerHTML = timeAgo(time)

function timeAgo(dateString) {
    dateString += "Z";
    const now = new Date();
    const date = new Date(dateString);
    const diff = (now - date) / 1000;

    if (diff < 60) {
        return `${Math.round(diff)} сек. назад`
    }
    else if (diff < 3600) {
        return `${Math.round(diff / 60)} мин. назад`
    }
    else if (diff < 86400) {
        return `${Math.round(diff / 3600)} ч. назад`
    }
    else if (diff < 2628000) {
        return `${Math.round(diff / 86400)} дн. назад`
    }
    else if (diff < 31540000){
        return `${Math.round(diff / 2628000)} мес. назад`
    }
    else {
        return `${date.toLocaleDateString("ru-RU")}`
    }
}



const answersList = document.getElementById('answerList')
async function start() {
    try {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Загрузка ответов...</p>`
        const response = await fetch('/api/answers')
        const answers = await response.json()
        render(answers)
    }
    catch (err) {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Ошибка при загрузке ответов</p>`
    }
}



function render(answers = []) {
    const questionid = answersList.dataset.questionid
    answers = answers.filter((answer) => answer.question_id === Number(questionid))
    if (answers.length === 0) {
        answersList.innerHTML = `<p style="text-align: center; margin-top: 20px">Нет ответов. Будьте первыми!</p>`
    }
    else {
        const html = answers.map(toHTML).join('')
        answersList.innerHTML = html
    }
}

function toHTML(answer) {
    const username = answersList.dataset.username
    return `<li class="questions-content-item">
        <div class="edit-wrapper">
            <button class="edit-btn" id="editBtn">
                <img src="/static/imgs/more.svg" alt="">
            </button>
            <div class="question-edit-container" id="editContainer">
                ${username === answer.username ? `
                <button type="button" class="delete-btn" id="deleteAnswerBtn" data-id="${answer.id}" data-owner="${answer.username}" data-questionId="${answer.question_id}">
                    <img src="/static/imgs/delete.svg" alt="">
                    Удалить
                </button>
                <button type="button" class="delete-btn" id="changeAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}" data-owner="${answer.username}">
                    <img src="/static/imgs/edit.svg" alt="">
                    Изменить
                </button>
                ` : `
                <button type="button" class="delete-btn" id="reportAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}">
                    <img src="/static/imgs/flag.svg" alt="">
                    Пожаловаться
                </button>
                `}
            </div>
        </div>
        <div class="questions-item-header">
            <a class="link" href="/profile/${answer.username}">${answer.name} (${answer.username})</a>
            <div>${timeAgo(answer.created_at)}</div>
        </div>
        <div class="answer-text short-text">${answer.text}</div>
        ${answer.text.split('\n').length > 3 ? `
            <button id="finishReadBtn" class="link read-more-btn">Читать далее</button>
            ` : ``}
        ${answer.images && answer.images.trim() !== '' ? `
            <div class="question-images scale">
                ${answer.images.split(',').map(src => `
                    <img src="${src}" alt="Изображение" class="question-image" onclick="openModal(this)">
                `).join('')}
            </div>
        ` : ''}
    </li>
    `
}

start()