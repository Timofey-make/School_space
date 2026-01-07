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

initCreateOverlay(createBtn, overlayContainer, closeBtn, () => {
    filesArrayCreateQuestion = []
    previewListCreateQuestion.innerHTML = ``
})



// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
let filesArrayCreateQuestion = []

if (imageInputCreateQuestion && previewListCreateQuestion) {
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
}

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