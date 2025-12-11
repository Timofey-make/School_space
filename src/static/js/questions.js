const questionsList = document.querySelector('#questionsList')
const seacrhInput = document.querySelector('#search')
const subjectSelect = document.getElementById('subject')
const gradeSelect = document.getElementById('grade')

let questions = []

async function start() {
    try {
        questionsList.innerHTML = '<p style="text-align: center;">Загрузка...</p>'
        const response = await fetch('/api/questions')
        questions = await response.json()
        render(questions)
    }
    catch (err) {
        questionsList.innerHTML = `<p style="text-align: center;">Ошибка при загрузке вопросов</p>`
    }
}

function applyFilters() {
    const value = seacrhInput.value.toLowerCase()
    const subject = subjectSelect.options[subjectSelect.selectedIndex].text.toLowerCase();
    const grade = gradeSelect.options[gradeSelect.selectedIndex].text.toLowerCase();

    let filtered = questions
    
    
    if (value) {
        filtered = filtered.filter((question) => question.text.toLowerCase().includes(value))
    }
    if (subject !== 'все предметы') {
        filtered = filtered.filter((question) => question.subject.toLowerCase().includes(subject))
    }
    if (grade !== 'все классы') {
        filtered = filtered.filter((question) => {
            let num = Number(question.grade)
            let min = Number(grade.split(' ')[0])
            let max = Number(grade.split(' ')[2])

            return num >= min && num <= max
        })
    }

    render(filtered)
}

seacrhInput.addEventListener('input', applyFilters)
subjectSelect.addEventListener('change', applyFilters)
gradeSelect.addEventListener('change', applyFilters)


function render(questions = []) {
    if (questions.length === 0) {
        questionsList.innerHTML = `<p style="text-align: center;">Вопросов нет</p>`
    }
    else {
        const html = questions.map(toHTML).join('')
        questionsList.innerHTML = html
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
                        <img src="${src}" alt="Изображение" class="question-image">
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

    filesArrayCreateQuestion = []
    previewListCreateQuestion.innerHTML = ``
})

start()


window.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })
    seacrhInput.value = ''
    document.getElementById('questionText').value = ''
});

// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
let filesArrayCreateQuestion = []

imageInputCreateQuestion.addEventListener('change', (event) => {
    const newFiles = Array.from(event.target.files)
    const MAX_FILES = 5
    const MAX_SIZE = 3 * 1024 * 1024
    const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

    newFiles.forEach(file => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            alert(`Файл ${file.name} не является изображением JPG/PNG/WebP`)
            return
        }
        if (file.size > MAX_SIZE) {
            alert(`Файл ${file.name} слишком большой (макс. 3 МБ)`)
            return
        }
        if (filesArrayCreateQuestion.length >= MAX_FILES) {
            alert(`Нельзя загрузить больше ${MAX_FILES} изображений`)
            return
        }
        filesArrayCreateQuestion.push(file)
    })
    renderPreviewsCreateQuestion()
})

function renderPreviewsCreateQuestion() {
    const html = filesArrayCreateQuestion.map((file, index) => {
        return `<li class="file-item" data-index="${index}">${file['name']}</li>`
    }).join('')
    previewListCreateQuestion.innerHTML = html
}

previewListCreateQuestion.addEventListener('click', (e) => {
    const item = e.target.closest('.file-item')
    if (!item) {
        return
    }

    const index = item.dataset.index
    filesArrayCreateQuestion.splice(index, 1);
    renderPreviewsCreateQuestion();
});

const formCreateQuestion = document.getElementById('formCreateQuestion');
formCreateQuestion.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData()
    formData.append('subject', formCreateQuestion.subject.value)
    formData.append('grade', formCreateQuestion.grade.value)
    formData.append('description', formCreateQuestion.description.value)


    filesArrayCreateQuestion.forEach(file => {
        formData.append('images', file)
    })

    try {
        const response = await fetch('/doadd', {
            method: 'POST',
            body: formData
        });

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const text = await response.text();
            console.log(text);
        }
    } catch (err) {
        console.error('Ошибка отправки формы:', err);
    }
});