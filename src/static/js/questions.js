import { toHTML, timeAgo, initCreateOverlay } from './utils.js';

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

function getTrigrams(str) {
    const trigrams = []
    if (str.length < 3) {
        return [str];
    }

    for (let i = 0; i <= str.length - 3; i++) {
        trigrams.push(str.slice(i, i + 3));
    }
    return trigrams;
}


function applyFilters() {
    const value = seacrhInput.value.toLowerCase()
    const subject = subjectSelect.options[subjectSelect.selectedIndex].text.toLowerCase();
    const grade = gradeSelect.options[gradeSelect.selectedIndex].text.toLowerCase();

    let filtered = questions
      
    if (value) {
        if (value.length < 3) {
            filtered = filtered.filter((question) => question.text.toLowerCase().includes(value))
        }
        else {
            filtered = filtered.filter((question) => {
                textTrigrams = getTrigrams(question.text.toLowerCase())
                valueTrigrams = getTrigrams(value)
                if (textTrigrams.length === 0 || valueTrigrams.length === 0) {
                    return false;
                }
                const textSet = new Set(textTrigrams);

                return valueTrigrams.some(tri => textSet.has(tri));
            })
        }
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

// create question overlay
const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

initCreateOverlay(createBtn, overlayContainer, closeBtn, () => {
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