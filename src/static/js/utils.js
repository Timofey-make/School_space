export function timeAgo(dateString) {
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

export function toHTML(question) {
    return `<li class="questions-content-item">
        <div class="questions-item-header">
            <a href="/profile/${question.owner_id}" class="item-header-name link">
                ${question.name} (${question.username})
            </a>
            <div class="item-header-subject">${question.subject}</div>
            <div class="item-header-grade">${question.grade} класс</div>
            <div class="item-header-time">${timeAgo(question.created_at)}</div>
            <div class="item-header-time">${question.edited ? 'Изменено' : '' }</div>
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
            <a class="btn" href="/question/${question.id}">Ответить</a>
        </div>
    </li>`;
}


//////// create question
let filesArrayCreateQuestion = []
export function initCreateOverlay(createBtn, overlayContainer, closeBtn) {
    if (!createBtn || !overlayContainer) return;

    createBtn.addEventListener('click', () => {
        overlayContainer.classList.add('active')
    })

    closeBtn.addEventListener('click', () => {
        overlayContainer.classList.remove('active')

        const selects = overlayContainer.querySelectorAll('select')
        selects.forEach((select) => {
            select.selectedIndex = 0;
        })

        const textarea = overlayContainer.querySelector('textarea')
        if (textarea) textarea.value = ''

        document.getElementById('previewListCreateQuestion').innerHTML = ``
        filesArrayCreateQuestion = []
    })
}

export function showNotification(text, notificationContainer) {
    notificationContainer.classList.remove('hide')
    notificationContainer.querySelector('p').textContent = text
    setTimeout(() => {
        notificationContainer.classList.add('hide');
    }, 3000)
}

function renderPreviewsCreateQuestion(filesArrayCreateQuestion) {
    const html = filesArrayCreateQuestion.map((file, index) => {
        return `<li class="file-item" data-index="${index}">${file['name']}</li>`
    }).join('')
    previewListCreateQuestion.innerHTML = html
}

export function uploadQuestionCreate(imageInputCreateQuestion, previewListCreateQuestion, notificationContainer) {
    if (imageInputCreateQuestion && previewListCreateQuestion && notificationContainer) {
        imageInputCreateQuestion.addEventListener('change', (event) => {
            const newFiles = Array.from(event.target.files)
            const MAX_FILES = 5
            const MAX_SIZE = 3 * 1024 * 1024
            const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']

            newFiles.forEach(file => {
                if (!ALLOWED_TYPES.includes(file.type)) {
                    showNotification(`Файл ${file.name} не является изображением JPG/PNG/WebP`, notificationContainer)
                    return
                }
                if (file.size > MAX_SIZE) {
                    showNotification(`Файл ${file.name} слишком большой (макс. 3 МБ)`, notificationContainer)
                    return
                }
                if (filesArrayCreateQuestion.length >= MAX_FILES) {
                    showNotification(`Нельзя загрузить больше ${MAX_FILES} изображений`, notificationContainer)
                    return
                }
                filesArrayCreateQuestion.push(file)
            })
            renderPreviewsCreateQuestion(filesArrayCreateQuestion)
        })

        


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

            formData.append('description', formCreateQuestion.description.value)
            formData.append('subject', formCreateQuestion.subject.value)
            formData.append('grade', formCreateQuestion.grade.value)
            


            filesArrayCreateQuestion.forEach(file => {
                formData.append('images', file)
            })

            try {
                const response = await fetch('/questions/doadd', {
                    method: 'POST',
                    body: formData
                });

                if (response.redirected) {  
                    localStorage.setItem('notification', 'Вопрос создан')
                    window.location.href = response.url;

                } else {
                    const text = await response.text();
                }
            } catch (err) {
                showNotification(`Ошибка отправки формы: ${err}`, notificationContainer)
                console.error('Ошибка отправки формы:', err);
            }
        });
    }
}



// modal windows images
export function openModal(img) {
    const modal = document.getElementById('imageModal')
    const modalImg = modal.querySelector('img')
    modalImg.src = img.src
    modal.classList.add('active')
}

window.openModal = openModal

export function closeModal() {
    document.getElementById('imageModal').classList.remove('active');
}

window.closeModal = closeModal


// search
function toSearchItemHTML(question) {
    return `<li class="search-result-item">
        <div class="questions-item-header">
            <a href="/profile/${question.username}" class="item-header-name link">
                ${question.name} (${question.username})
            </a>
            <div class="item-header-subject">${question.subject}</div>
            <div class="item-header-grade">${question.grade} класс</div>
            <div class="item-header-time">${timeAgo(question.created_at)}</div>
        </div>
        <div class="questions-item-body">${question.text}</div>

        

        <div class="questions-item-footer">
            <a class="btn" href="/question/${question.id}">Ответить</a>
        </div>
    </li>`;
}

function render(questions = []) {
    if (questions.length === 0) {
        searchList.innerHTML = `<p style="text-align: center;">Ничего не найдено</p>`
    }
    else {
        const html = questions.map(toSearchItemHTML).join('')
        searchList.innerHTML = html
    }
}

export function getTrigrams(str) {
    const trigrams = []
    if (str.length < 3) {
        return [str];
    }

    for (let i = 0; i <= str.length - 3; i++) {
        trigrams.push(str.slice(i, i + 3));
    }
    return trigrams;
}


export function searchResult(searchEl, searchList) {
    searchEl.addEventListener('input', async (e) => {
        const value = e.target.value.trim()
        if (!value) {
            searchList.classList.remove('active')
            searchList.innerHTML = ''
            return
        }

        searchList.classList.add('active')
        try {
            const response = await fetch('/api/questions')
            let questions = await response.json()
            let filtered = questions
            if (value.length < 3) {
                filtered = filtered.filter((question) => question.text.toLowerCase().includes(value.toLowerCase()))
            }
            else {
                filtered = filtered.filter((question) => {
                    let textTrigrams = getTrigrams(question.text.toLowerCase())
                    let valueTrigrams = getTrigrams(value)
                    if (textTrigrams.length === 0 || valueTrigrams.length === 0) {
                        return false;
                    }
                    const textSet = new Set(textTrigrams);

                    return valueTrigrams.some(tri => textSet.has(tri));
                })
            }
            render(filtered)
        }
        catch (err) {
            searchList.innerHTML = `<p style="text-align: center;">Ошибка при загрузке вопросов</p>`
            console.log(err)
        }
    })
}
