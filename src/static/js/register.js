const registerForm = document.getElementById('registerForm')

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault()

    const registerData = new FormData(e.target)

    const response = await fetch("/doregister", {
        method: "POST",
        body: registerData
    });
    console.log('adad')

    if (response.redirected) {
        window.location.href = response.url
    } else {
        const errorText = await response.json()
        document.getElementById('errorMessage').innerHTML = errorText.error
    }
})