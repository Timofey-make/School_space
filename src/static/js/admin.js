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

const questionImages = document.getElementById('questionImages')
const paths = questionImages.dataset.images.split(',')
const htmlImages = paths.map((path) => {
    return `<img src="${path}" alt="Изображение вопроса" onclick="openModal(this)">`
})
questionImages.innerHTML = htmlImages

function openModal(img) {
    const modal = document.getElementById('imageModal')
    const modalImg = modal.querySelector('img')
    modalImg.src = img.src
    modal.classList.add('active')
}

function closeModal() {
    document.getElementById('imageModal').classList.remove('active');
}