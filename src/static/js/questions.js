import { toHTML, timeAgo, initCreateOverlay, uploadQuestionCreate, getTrigrams, showNotification } from './utils.js';

const questionsList = document.querySelector('#questionsList')
const seacrhInput = document.querySelector('#search')
const subjectSelect = document.getElementById('subject')
const gradeSelect = document.getElementById('grade')

let questions = []

async function start() {
    try {
        questionsList.innerHTML = '<p style="text-align: center;">Загрузка вопросов...</p>'
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
        if (value.length < 3) {
            filtered = filtered.filter((question) => question.text.toLowerCase().includes(value))
        }
        else {
            filtered = filtered.filter((question) => {
                const textTrigrams = getTrigrams(question.text.toLowerCase())
                const valueTrigrams = getTrigrams(value)
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

initCreateOverlay(createBtn, overlayContainer, closeBtn)



start()


window.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        select.selectedIndex = 0;
    })
    seacrhInput.value = ''
    document.getElementById('questionText').value = ''

    const msg = localStorage.getItem('notification')
    if (msg) {
        showNotification(msg, document.getElementById('notification'))
        localStorage.removeItem('notification')
    }    
});


// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
const notificationContainer = document.getElementById('notification')
uploadQuestionCreate(imageInputCreateQuestion, previewListCreateQuestion, notificationContainer)


// close modals
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    const overlays = document.querySelectorAll('.overlay.active')
    overlays.forEach(overlay => {
        overlay.classList.remove('active');
    });
    const notification = document.getElementById('notification')
    if (notification) {
        document.getElementById('notification').classList.add('hide')
    }
  }
});