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

const handleAccountChanges = (formName) => {
    const elements = document.querySelectorAll(`[data-account-form="${formName}"]`)
    elements.forEach(element => {
        let endpoint = element.dataset.accountEndpoint
        if (endpoint) {
            const context = element.dataset.accountContext
            if (context) {
                if (endpoint.includes('?')) {
                    endpoint = `${endpoint}&context=${context}`
                } else {
                    endpoint = `${endpoint}?context=${context}`
                }
            }

            htmx.ajax('GET', endpoint, {
                target: `#${element.id}`,
                swap: 'outerHTML',
            });
        }
    })
}