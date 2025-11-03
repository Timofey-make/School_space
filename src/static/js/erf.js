function toHTML(answer) {
    const username = answersList.dataset.username
    if (username === answer.username) {
        if (answer.text.split('\n').length > 3) {
            return `<li class="questions-content-item">
                <div class="edit-wrapper">
                    <button class="edit-btn" id="editBtn">
                        <img src="/static/imgs/more.svg" alt="">
                    </button>
                    <div class="question-edit-container" id="editContainer">
                        <button type="button" class="delete-btn" id="deleteAnswerBtn" data-id="${answer.id}" data-owner="${answer.username}" data-questionId="${answer.question_id}">
                            <img src="/static/imgs/delete.svg" alt="">
                            Удалить
                        </button>
                        <button type="button" class="delete-btn" id="changeAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}" data-owner="${answer.username}">
                            <img src="/static/imgs/edit.svg" alt="">
                            Изменить
                        </button>
                    </div>
                </div>

                <div class="questions-item-header">
                    <a class="link" href="/profile/${answer.username}">${answer.name} (${answer.username})</a>
                    <div>${timeAgo(answer.created_at)}</div>
                </div>
                <div class="answer-text short-text">${answer.text}</div>
                ${answer.images.split(',') && answer.images.split(',').length > 0 ? `
                <div class="question-images scale">
                    ${answer.images.split(',').map(src => `
                        <img src="${src}" alt="Изображение вопроса" class="question-image" onclick="openModal(this)">
                    `).join('')}
                </div>
            ` : ''}

                <button id="finishReadBtn" class="link read-more-btn">Читать далее</button>
            </li>
            `
        }
        else {
            return `<li class="questions-content-item">
                <div class="edit-wrapper">
                    <button class="edit-btn" id="editBtn">
                        <img src="/static/imgs/more.svg" alt="">
                    </button>
                    <div class="question-edit-container" id="editContainer">
                        <button type="button" class="delete-btn" id="deleteAnswerBtn" data-id="${answer.id}" data-owner="${answer.username}" data-questionId="${answer.question_id}">
                            <img src="/static/imgs/delete.svg" alt="">
                            Удалить
                        </button>
                        <button type="button" class="delete-btn" id="changeAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}" data-owner="${answer.username}">
                            <img src="/static/imgs/edit.svg" alt="">
                            Изменить
                        </button>
                    </div>
                </div>

                <div class="questions-item-header">
                    <a class="link" href="/profile/${answer.username}">${answer.name} (${answer.username})</a>
                    <div>${timeAgo(answer.created_at)}</div>
                </div>
                <div class="answer-text short-text">${answer.text}</div>
                ${answer.images.split(',') && answer.images.split(',').length > 0 ? `
                <div class="question-images scale">
                    ${answer.images.split(',').map(src => `
                        <img src="${src}" alt="Изображение вопроса" class="question-image" onclick="openModal(this)">
                    `).join('')}
                </div>
                <div class="image-modal" id="imageModal" onclick="closeModal()">
                    <img src="" alt="Preview">
                </div>
            ` : ''}
            </li>
            `
        }
    }
    else {
        if (answer.text.split('\n').length > 3) {
            return `<li class="questions-content-item">
                <div class="edit-wrapper">
                    <button class="edit-btn" id="editBtn">
                        <img src="/static/imgs/more.svg" alt="">
                    </button>
                    <div class="question-edit-container" id="editContainer">
                        <button type="button" class="delete-btn" id="reportAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}">
                            <img src="/static/imgs/flag.svg" alt="">
                            Пожаловаться
                        </button>
                    </div>
                </div>

                <div class="questions-item-header">
                    <a class="link" href="/profile/${answer.username}">${answer.name} (${answer.username})</a>
                    <div>${timeAgo(answer.created_at)}</div>
                </div>
                <div class="answer-text short-text">${answer.text}</div>
                <button id="finishReadBtn" class="link read-more-btn">Читать далее</button>
                ${answer.images.split(',') && answer.images.split(',').length > 0 ? `
                <div class="question-images scale">
                    ${answer.images.split(',').map(src => `
                        <img src="${src}" alt="Изображение вопроса" class="question-image" onclick="openModal(this)">
                    `).join('')}
                </div>
            ` : ''}
            </li>
            `
        }
        else {
            return `<li class="questions-content-item">
                <div class="edit-wrapper">
                    <button class="edit-btn" id="editBtn">
                        <img src="/static/imgs/more.svg" alt="">
                    </button>
                    <div class="question-edit-container" id="editContainer">
                        <button type="button" class="delete-btn" id="reportAnswerBtn" data-id="${answer.id}" data-questionId="${answer.question_id}">
                            <img src="/static/imgs/flag.svg" alt="">
                            Пожаловаться
                        </button>
                    </div>
                </div>

                <div class="questions-item-header">
                    <a class="link" href="/profile/${answer.username}">${answer.name} (${answer.username})</a>
                    <div>${timeAgo(answer.created_at)}</div>
                </div>
                <div class="answer-text short-text">${answer.text}</div>
                ${answer.images.split(',') && answer.images.split(',').length > 0 ? `
                <div class="question-images scale">
                    ${answer.images.split(',').map(src => `
                        <img src="${src}" alt="Изображение вопроса" class="question-image" onclick="openModal(this)">
                    `).join('')}
                </div>
            ` : ''}
            </li>
            `
        }
    } 
}