const authForm = document.getElementById('loginForm')
const inputs = document.querySelectorAll('input')
inputs.forEach(input => {
    input.addEventListener('click', () => {
        errorMessage.innerText = ""
    })
})


authForm.addEventListener('submit', async (e) => {
    e.preventDefault()

    const formData = new FormData(e.target)
    const response = await fetch("/dologin", {
        method: "POST",
        body: formData
    });


    if (response.redirected) {
        window.location.href = response.url
    } else {
        const data = await response.json();
        document.getElementById('password').value = ''
        document.getElementById("errorMessage").innerText = data.error
    }
})