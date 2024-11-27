const generateRandomUserAccountPassword = (event) => {
    const randownPassword = generateRandomPassword(16)
    const passwordForm = event.target.closest('form')
    const newPassword1 = passwordForm.elements.new_password1
    
    newPassword1.value = randownPassword
    passwordForm.elements.new_password2.value = randownPassword
    
    newPassword1.setAttribute('type', 'text')
    newPassword1.addEventListener('keyup', () => {
        newPassword1.setAttribute('type', 'password')
    }, { once: true });

    const inputEvent = new Event('input')
    newPassword1.dispatchEvent(inputEvent)
}