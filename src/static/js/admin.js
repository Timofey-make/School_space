adminForm = document.getElementById('adminForm')

adminForm.addEventListener('submit', async (e) => {
    e.preventDefault()


    const adminFormData = new FormData(e.target)
    const response = await fetch("/admin/add", {
        method: "POST",
        body: adminFormData
    });
    if (response.redirected) {
        window.location.href = response.url;
    }
    else {
        const data = await response.json();
        document.getElementById('adminInput').value = ''
        document.getElementById("errorMessage").innerText = data.error
    }
})

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

// render images question admin
adminQuestionImages = document.querySelectorAll('#adminQuestionImages')


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
adminAnswerImages = document.querySelectorAll('#adminAnswerImages')


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
            }
        } catch (err) {
            console.error('Ошибка отправки формы:', err);
        }
    });
}

function openModal(img) {
    const modal = document.getElementById('imageModal')
    const modalImg = modal.querySelector('img')
    modalImg.src = img.src
    modal.classList.add('active')
}

function closeModal() {
    document.getElementById('imageModal').classList.remove('active');
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