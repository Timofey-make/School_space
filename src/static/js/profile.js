import { toHTML, initCreateOverlay } from './utils.js';

const profileQuestionsContainer = document.getElementById('profileQuestionsContainer')

async function start() {
    let profileUsername = profileQuestionsContainer.dataset.username
    try {
    profileQuestionsContainer.innerHTML = '<p style="text-align: center;">Загрузка...</p>'
        const response = await fetch('/api/questions')
        let questions = await response.json()
        questions = questions.filter((question) => question.username === profileUsername)
        render(questions)
    }
    catch (err) {
        profileQuestionsContainer.innerHTML = `<p style="text-align: center;">Ошибка при загрузке вопросов</p>`
    }
}

function render(questions = []) {
    if (questions.length === 0) {
        profileQuestionsContainer.innerHTML = `<p style="text-align: center;">У пользователя нет вопросов</p>`
    }
    else {
        const html = questions.map(toHTML).join('')
        profileQuestionsContainer.innerHTML = html
    }
}



start()


// create question overlay
const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

initCreateOverlay(createBtn, overlayContainer, closeBtn)



// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
uploadQuestionCreate(imageInputCreateQuestion, previewListCreateQuestion)




// delete account
const deleteProfileElement = document.getElementById('deleteProfile')
const overlaySureProfileDelete = document.getElementById('overlaySureProfileDelete')
const sureCloseDeleteProfileBtn = document.getElementById('sureCloseDeleteProfileBtn')
const sureCancelProfileDeleteBtn = document.getElementById('sureCancelProfileDeleteBtn')

if (deleteProfileElement && overlaySureProfileDelete && sureCloseDeleteProfileBtn) {
    deleteProfileElement.addEventListener('click', (e) => {
        overlaySureProfileDelete.classList.add('active')
    })
    sureCancelProfileDeleteBtn.addEventListener('click', () => {
        overlaySureProfileDelete.classList.remove('active')
    })
    sureCloseDeleteProfileBtn.addEventListener('click', () => {
        overlaySureProfileDelete.classList.remove('active')
    })
}


window.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })
    document.getElementById('search').value = ''
    document.getElementById('questionText').value = ''
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.checked = false;
    });
});