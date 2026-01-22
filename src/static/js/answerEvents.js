import { initCreateOverlay, openModal, closeModal, uploadQuestionCreate, timeAgo, searchResult } from './utils.js';

// create question overlay
const createBtn = document.getElementById('create')
const overlayContainer = document.getElementById('overlayCreate')
const closeBtn = document.getElementById('close')

initCreateOverlay(createBtn, overlayContainer, closeBtn)



const editBtn = document.getElementById('editBtn')
const editContainer = document.getElementById('editContainer')
if (editBtn && editContainer) {
    editBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        const activeContainers = document.querySelectorAll('.question-edit-container.active');
        activeContainers.forEach(active => {
            if (active !== editContainer) active.classList.remove('active');
        });
        editContainer.classList.toggle('active');
    })
}

const answersList = document.getElementById('answerList')
answersList.addEventListener('click', (e) => {
    const editBtn = e.target.closest('#editBtn')
    const reportAnswerBtn = e.target.closest('#reportAnswerBtn')
    const deleteAnswerBtn = e.target.closest('#deleteAnswerBtn')
    const changeAnswerBtn = e.target.closest('#changeAnswerBtn')
    const finishReadBtn = e.target.closest('#finishReadBtn')

    
    if (editBtn) {
        const container = editBtn.closest('.questions-content-item')
                            .querySelector('.question-edit-container');
        
        document.querySelectorAll('.question-edit-container.active')
                .forEach(active => {
                    if (active !== container) {
                        active.classList.remove('active');
                    }
                });
        
        container.classList.toggle('active');
        e.stopPropagation();
        return;
    }
    
    if (reportAnswerBtn) {
        const overlayReportAnswerContainer = document.getElementById('overlayReportAnswerContainer');
        const closeReportAnswerContainerBtn = document.getElementById('closeReportAnswerContainerBtn');
        
        if (closeReportAnswerContainerBtn && closeReportAnswerContainerBtn) {
            overlayReportAnswerContainer.classList.add('active');

            const reportAnswerId = document.getElementById('reportAnswerId')
            const reportAnswerQuestionId = document.getElementById('reportAnswerQuestionId')

            reportAnswerId.value = reportAnswerBtn.dataset.id
            reportAnswerQuestionId.value = reportAnswerBtn.dataset.questionid
            

            
            closeReportAnswerContainerBtn.onclick = () => {
                overlayReportAnswerContainer.classList.remove('active');
            };
        }
    }
    
    if (deleteAnswerBtn) {
        const overlaySureAnswerDelete = document.getElementById('overlaySureAnswerDelete')
        const sureCancelAnswerBtn = document.getElementById('sureCancelAnswerBtn')
        const sureCloseAnswerBtn = document.getElementById('sureCloseAnswerBtn')

        if (overlaySureAnswerDelete && sureCancelAnswerBtn && sureCloseAnswerBtn) {
            overlaySureAnswerDelete.classList.add('active')

            const deleteAnswerOwner = document.getElementById('deleteAnswerOwner')
            const deleteAnswerId = document.getElementById('deleteAnswerId')
            const deleteAnswerQuestionId = document.getElementById('deleteAnswerQuestionId')
            deleteAnswerOwner.value = deleteAnswerBtn.dataset.owner
            deleteAnswerId.value = deleteAnswerBtn.dataset.id
            deleteAnswerQuestionId.value = deleteAnswerBtn.dataset.questionid

            sureCancelAnswerBtn.addEventListener('click', () => {
                overlaySureAnswerDelete.classList.remove('active')
            })
            sureCloseAnswerBtn.addEventListener('click', () => {
                overlaySureAnswerDelete.classList.remove('active')
            })
        }
    }
    if (changeAnswerBtn) {
        const overlayChangeAnswerContainer = document.getElementById('overlayChangeAnswerContainer')
        const closeChangeAnswerContainerBtn = document.getElementById('closeChangeAnswerContainerBtn')
        if (overlayChangeAnswerContainer && closeChangeAnswerContainerBtn) {
            overlayChangeAnswerContainer.classList.add('active')

            const changeAnswerOwner = document.getElementById('changeAnswerOwner')
            const changeAnswerId = document.getElementById('changeAnswerId')
            const changeQuestionId = document.getElementById('changeQuestionId')
            changeAnswerOwner.value = changeAnswerBtn.dataset.owner
            changeAnswerId.value = changeAnswerBtn.dataset.id
            changeQuestionId.value = changeAnswerBtn.dataset.questionid

            const answerEl = e.target.closest('.questions-content-item')
            formChangeAnswer.new_description.value = answerEl.querySelector('.answer-text').innerHTML
            images = answerEl.querySelector('.question-images')
            if (images) {
                images = images.querySelectorAll('img')
                filesArrayChangeAnswer = []
                previewListChangeAnswer.innerHTML = ``
                getFilesFromImages(images).then(files => {
                    filesArrayChangeAnswer = files
                    renderPreviewsChangeAnswer()
                });
            }


            

            closeChangeAnswerContainerBtn.addEventListener('click', () => {
                overlayChangeAnswerContainer.classList.remove('active')

                const textarea = overlayChangeAnswerContainer.querySelector('textarea')
                if (textarea) textarea.value = ''

                filesArrayChangeAnswer = []
                previewListChangeAnswer.innerHTML = ``
            })
        }
    }

    if (finishReadBtn) {
        const container = finishReadBtn.closest('.questions-content-item')
        const textBlock = container.querySelector('.answer-text')

        if (textBlock.classList.contains('short-text')) {
            textBlock.classList.remove('short-text')
            finishReadBtn.textContent = 'Скрыть'
        }
        else {
            textBlock.classList.add('short-text')
            finishReadBtn.textContent = 'Читать далее'
        }
    }
})


document.addEventListener('click', (e) => {
    const activeContainers = document.querySelectorAll('.question-edit-container.active');

    activeContainers.forEach(container => {
        container.classList.remove('active');
    });
    searchList.classList.remove('active')
});




const deleteQuestionBtn = document.getElementById('deleteQuestionBtn')
const overlaySureQuestionDelete = document.getElementById('overlaySureQuestionDelete')
const sureCancelQuestionBtn = document.getElementById('sureCancelQuestionBtn')
const sureCloseQuestionBtn = document.getElementById('sureCloseQuestionBtn')

if (deleteQuestionBtn && overlaySureQuestionDelete && sureCancelQuestionBtn && sureCloseQuestionBtn) {
    deleteQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.add('active')
    })
    sureCancelQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.remove('active')
    })
    sureCloseQuestionBtn.addEventListener('click', () => {
        overlaySureQuestionDelete.classList.remove('active')
    })
}

async function getFilesFromImages(nodeList) {
  const files = [];

  for (let i = 0; i < nodeList.length; i++) {
    const img = nodeList[i];
    const url = img.src;


    const decodedUrl = decodeURIComponent(url);
    const filename = decodedUrl.split('/').pop().split('?')[0];

    const response = await fetch(url);
    const blob = await response.blob();

    const file = new File([blob], filename, { type: blob.type });
    files.push(file);
  }

  return files;
}


const changeQuestionBtn = document.getElementById('changeQuestionBtn')
const overlayChangeQuestionContainer = document.getElementById('overlayChangeQuestionContainer')
const closeChangeQuestionContainerBtn = document.getElementById('closeChangeQuestionContainerBtn')
if (changeQuestionBtn && overlayChangeQuestionContainer && closeChangeQuestionContainerBtn) {
    changeQuestionBtn.addEventListener('click', () => {
        overlayChangeQuestionContainer.classList.add('active')
        formChangeQuestion.new_description.value = document.getElementById('questionContent').innerHTML
        formChangeQuestion.subject.value = document.getElementById('questionSubject').innerHTML
        formChangeQuestion.grade.value = document.getElementById('questionGrade').innerHTML.split(' ')[0]
        images = document.getElementById('questionImages')
        if (images) {
            images = images.querySelectorAll('img')
            filesArrayChangeQuestion = []
            previewListChangeQuestion.innerHTML = ``
            getFilesFromImages(images).then(files => {
                filesArrayChangeQuestion = files
                renderPreviewsChangeQuestion()
            });
        }
    })
    closeChangeQuestionContainerBtn.addEventListener('click', () => {
        overlayChangeQuestionContainer.classList.remove('active')

        const selects = overlayChangeQuestionContainer.querySelectorAll('select')
        selects.forEach((select) => {
            select.selectedIndex = 0;
        })

        const textarea = overlayChangeQuestionContainer.querySelector('textarea')
        if (textarea) textarea.value = ''

        filesArrayChangeQuestion = []
        previewListChangeQuestion.innerHTML = ``
    })
}


const reportQuestionBtn = document.getElementById('reportQuestionBtn')
const overlayReportQuestionContainer = document.getElementById('overlayReportQuestionContainer')
const closeReportQuestionContainerBtn = document.getElementById('closeReportQuestionContainerBtn')
if (reportQuestionBtn && overlayReportQuestionContainer) {
    reportQuestionBtn.addEventListener('click', () => {
        overlayReportQuestionContainer.classList.add('active')
    })
    closeReportQuestionContainerBtn.addEventListener('click', () => {
        overlayReportQuestionContainer.classList.remove('active')
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.checked = false;
        });
    })
}

// Поле ответа
const textarea = document.getElementById('answerTextArea')
if (textarea) {
    textarea.addEventListener("input", () => {
        textarea.style.height = "auto"
        textarea.style.height = Math.min(textarea.scrollHeight, 1000) + "px";
    });
} 



// upload question create
const imageInputCreateQuestion = document.getElementById('imageInputCreateQuestion')
const previewListCreateQuestion = document.getElementById('previewListCreateQuestion')
uploadQuestionCreate(imageInputCreateQuestion, previewListCreateQuestion)

// change question upload
const imageInputChangeQuestion = document.getElementById('imageInputChangeQuestion')
const previewListChangeQuestion = document.getElementById('previewListChangeQuestion')
let filesArrayChangeQuestion = []

if (imageInputChangeQuestion && previewListChangeQuestion) {
    imageInputChangeQuestion.addEventListener('change', (event) => {
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
            if (filesArrayChangeQuestion.length >= MAX_FILES) {
                alert(`Нельзя загрузить больше ${MAX_FILES} изображений`)
                return
            }
            filesArrayChangeQuestion.push(file)
        })
        renderPreviewsChangeQuestion()
    })

    function renderPreviewsChangeQuestion() {
        const html = filesArrayChangeQuestion.map((file, index) => {
            return `<li class="file-item" data-index="${index}">${file['name']}</li>`
        }).join('')
        previewListChangeQuestion.innerHTML = html
    }

    previewListChangeQuestion.addEventListener('click', (e) => {
        const item = e.target.closest('.file-item')
        if (!item) {
            return
        }

        const index = item.dataset.index
        filesArrayChangeQuestion.splice(index, 1);
        renderPreviewsChangeQuestion();
    });

    const formChangeQuestion = document.getElementById('formChangeQuestion');
    formChangeQuestion.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData()
        formData.append('subject', formChangeQuestion.subject.value)
        formData.append('grade', formChangeQuestion.grade.value)
        formData.append('new_description', formChangeQuestion.new_description.value)
        formData.append('id', formChangeQuestion.id.value)


        filesArrayChangeQuestion.forEach(file => {
            formData.append('images', file)
        })


        try {
            const response = await fetch('/questions/change', {
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


// answer upload create
const imageInputCreateAnswer = document.getElementById('imageInputCreateAnswer')
const previewListCreateAnswer = document.getElementById('previewListCreateAnswer')
let filesArrayCreateAnswer = []

if (imageInputCreateAnswer && previewListCreateAnswer) {
    imageInputCreateAnswer.addEventListener('change', (event) => {
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
            if (filesArrayCreateAnswer.length >= MAX_FILES) {
                alert(`Нельзя загрузить больше ${MAX_FILES} изображений`)
                return
            }
            filesArrayCreateAnswer.push(file)
        })
        renderPreviewsCreateAnswer()
    })

    function renderPreviewsCreateAnswer() {
        const html = filesArrayCreateAnswer.map((file, index) => {
            return `<li class="file-item" data-index="${index}">${file['name']}</li>`
        }).join('')
        previewListCreateAnswer.innerHTML = html
    }

    previewListCreateAnswer.addEventListener('click', (e) => {
        const item = e.target.closest('.file-item')
        if (!item) {
            return
        }

        const index = item.dataset.index
        filesArrayCreateAnswer.splice(index, 1);
        renderPreviewsCreateAnswer();
    });

    const formCreateAnswer = document.getElementById('formCreateAnswer');
    formCreateAnswer.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formDataAnswer = new FormData()
        formDataAnswer.append('comment', formCreateAnswer.comment.value)
        formDataAnswer.append('id', formCreateAnswer.id.value)

        filesArrayCreateAnswer.forEach(file => {
            formDataAnswer.append('images', file)
        })


        try {
            const response = await fetch('/answers/addcomment', {
                method: 'POST',
                body: formDataAnswer
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


// change answer upload
const imageInputChangeAnswer = document.getElementById('imageInputChangeAnswer')
const previewListChangeAnswer = document.getElementById('previewListChangeAnswer')
let filesArrayChangeAnswer = []

if (imageInputChangeAnswer && previewListChangeAnswer) {
    imageInputChangeAnswer.addEventListener('change', (event) => {
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
            if (filesArrayChangeAnswer.length >= MAX_FILES) {
                alert(`Нельзя загрузить больше ${MAX_FILES} изображений`)
                return
            }
            filesArrayChangeAnswer.push(file)
        })
        renderPreviewsChangeAnswer()
    })


    function renderPreviewsChangeAnswer() {
        const html = filesArrayChangeAnswer.map((file, index) => {
            return `<li class="file-item" data-index="${index}">${file['name']}</li>`
        }).join('')
        previewListChangeAnswer.innerHTML = html
    }

    previewListChangeAnswer.addEventListener('click', (e) => {
        const item = e.target.closest('.file-item')
        if (!item) {
            return
        }

        const index = item.dataset.index
        filesArrayChangeAnswer.splice(index, 1);
        renderPreviewsChangeAnswer();
    });

    const formChangeAnswer = document.getElementById('formChangeAnswer');
    formChangeAnswer.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formDataAnswer = new FormData()
        formDataAnswer.append('comment', formChangeAnswer.new_description.value)
        formDataAnswer.append('owner', formChangeAnswer.owner.value)
        formDataAnswer.append('id', formChangeAnswer.id.value)
        formDataAnswer.append('questionId', formChangeAnswer.questionId.value)

        filesArrayChangeAnswer.forEach(file => {
            formDataAnswer.append('images', file)
        })


        try {
            const response = await fetch('/answers/change_answer', {
                method: 'POST',
                body: formDataAnswer
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
    document.getElementById('answerTextArea').value = ''
});


// search
const searchEl = document.getElementById('search')
const searchList = document.getElementById('searchList')
searchResult(searchEl, searchList)
    
// ${question.images && question.images.length > 0 ? `
//             <div class="question-images">
//                 ${question.images.map(src => `
//                     <img src="${src}" alt="Изображение" class="question-image">
//                 `).join('')}
//             </div>
//         ` : ''}