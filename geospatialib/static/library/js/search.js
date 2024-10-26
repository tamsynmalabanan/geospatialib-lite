const searchLibrary = (query) => {
    const form = document.querySelector('form[hx-get="/htmx/library/search/"]')
    form.elements.query.value = query
    
    const event = new CustomEvent('submit')
    form.dispatchEvent(event)
}

document.addEventListener('htmx:configRequest', (event) => {
    const detail = event.detail
    if (detail.path === "/htmx/library/search/" && window.location.pathname === '/') {
        const params = detail.parameters
        pushParamsToURL(params)
    }
})