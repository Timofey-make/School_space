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
            <a href="/profile/${question.username}" class="item-header-name link">
                ${question.name} (${question.username})
            </a>
            <div class="item-header-subject">${question.subject}</div>
            <div class="item-header-grade">${question.grade} класс</div>
            <div class="item-header-time">${timeAgo(question.created_at)}</div>
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
            <a class="btn" href="question/${question.id}">Ответить</a>
        </div>
    </li>`;
}


////////
export function initCreateOverlay(createBtn, overlayContainer, closeBtn, onclose) {
    console.log('УраААА')
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

        onclose()

    })
}