adminForm = document.getElementById('adminForm')

adminForm.addEventListener('submit', async (e) => {
    e.preventDefault()


    const adminForm = new FormData(e.target)
    const response = await fetch("/admin/add", {
        method: "POST",
        body: adminForm
    });

    if (response.redirected) {
        window.location.href = response.url
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

const questionImages = document.getElementById('questionImages')
if (questionImages) {
    const paths = questionImages.dataset.images.split(',')
    const htmlImages = paths.map((path) => {
        return `<img src="${path}" alt="Изображение вопроса" onclick="openModal(this)">`
    })
    questionImages.innerHTML = htmlImages

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