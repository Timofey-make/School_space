import { initCreateOverlay, uploadQuestionCreate, openModal, closeModal, searchResult, showNotification } from './utils.js';

adminForm = document.getElementById('adminForm')

adminForm.addEventListener('submit', async (e) => {
    e.preventDefault()


    const adminFormData = new FormData(e.target)
    const response = await fetch("/admin/add", {
        method: "POST",
        body: adminFormData
    });
    if (response.redirected) {
        localStorage.setItem('notification', `Пользователь ${adminFormData.get('target_username')} назначен админом`)
        window.location.href = response.url;
    }
    else {
        const data = await response.json();
        document.getElementById('adminInput').value = ''
        showNotification(data.error, document.getElementById('notification'))
    }
})

// create question overlay
const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

initCreateOverlay(createBtn, overlayContainer, closeBtn)

// render images question admin
let adminQuestionImages = document.querySelectorAll('#adminQuestionImages')


if (adminQuestionImages) {
    adminQuestionImages.forEach((reportQ) => {
        let srcImages = reportQ.dataset.images.split(',')
        srcImages = srcImages.map((src) => {
            return `<img src="${src}" alt="Изображение" class="question-image" onclick="openModal(this)">`
        }).join('')
        reportQ.innerHTML = srcImages
    })
}
// render images answer admin
let adminAnswerImages = document.querySelectorAll('#adminAnswerImages')

if (adminAnswerImages) {
    adminAnswerImages.forEach((reportA) => {
        let srcImages = reportA.dataset.images.split(',')
        srcImages = srcImages.map((src) => {
            return `<img src="${src}" alt="Изображение" class="question-image" onclick="openModal(this)">`
        }).join('')
        reportA.innerHTML = srcImages
    })
}


// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
const notificationContainer = document.getElementById('notification')
uploadQuestionCreate(imageInputCreateQuestion, previewListCreateQuestion, notificationContainer)



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
    
    const msg = localStorage.getItem('notification')
    if (msg) {
        showNotification(msg, document.getElementById('notification'))
        localStorage.removeItem('notification')
    }
});

// search
const searchEl = document.getElementById('search')
const searchList = document.getElementById('searchList')
searchResult(searchEl, searchList)

document.addEventListener('click', (e) => {
    searchList.classList.remove('active')
})