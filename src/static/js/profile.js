const profileQuestionsContainer = document.getElementById('profileQuestionsContainer')

async function start() {
    profileUsername = profileQuestionsContainer.dataset.username
    try {
    profileQuestionsContainer.innerHTML = '<p style="text-align: center;">Загрузка...</p>'
        const response = await fetch('/api/questions')
        questions = await response.json()
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

function toHTML(question) {
    return `<li class="questions-content-item">
            <div class="questions-item-header">
                <a href="/profile/${question.username}" class="item-header-name link">
                    ${question.name} (${question.username})
                </a>
                <div class="item-header-subject">${question.subject}</div>
                <div class="item-header-grade">${question.grade} класс</div>
                <div class="item-header-time">${timeAgo(question.created_at)}</div>
            </div>
            <div class="questions-item-body">${question.text}</div>

            ${question.images && question.images.length > 0 ? `
                <div class="question-images">
                    ${question.images.map(src => `
                        <img src="${src}" alt="Изображение вопроса" class="question-image">
                    `).join('')}
                </div>
            ` : ''}

            <div class="questions-item-footer">
                <a class="btn" href="question/${question.id}">Ответить</a>
            </div>
        </li>`
}


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

start()

const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

if (createBtn) {
    createBtn.addEventListener('click', () => {
        overlayContainer.classList.add('active')
    })
}

closeBtn.addEventListener('click', () => {
    overlayContainer.classList.remove('active')

    const selects = overlayContainer.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })

    const textarea = overlayContainer.querySelector('textarea')
    if (textarea) textarea.value = ''

    filesArray = []
    previewList.innerHTML = ``
})



// upload
const imageInput = document.getElementById('imageInput')
const previewList = document.getElementById('previewList')
let filesArray = []

imageInput.addEventListener('change', (event) => {
    filesArray.push(...event.target.files)
    renderPreviews()
})

function renderPreviews() {
    const html = filesArray.map((file, index) => {
        return `<li class="file-item" data-index="${index}">${file['name']}</li>`
    }).join('')
    previewList.innerHTML = html
}

previewList.addEventListener('click', (e) => {
    const item = e.target.closest('.file-item')
    if (!item) {
        return
    }

    const index = item.dataset.index
    filesArray.splice(index, 1);
    renderPreviews();
});

const form = document.querySelector('.create-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData()
    formData.append('subject', form.subject.value)
    formData.append('grade', form.grade.value)
    formData.append('description', form.description.value)


    filesArray.forEach(file => {
        formData.append('images', file)
    })

    try {
        const response = await fetch('/doadd', {
            method: 'POST',
            body: formData
        });

        if (response.redirected) {
            window.location.href = response.url; // редирект при успешной отправке
        } else {
            const text = await response.text();
            console.log(text);
        }
    } catch (err) {
        console.error('Ошибка отправки формы:', err);
    }
});