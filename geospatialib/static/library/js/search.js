const searchEndpoint = "/htmx/library/search/"

const searchResultsScrollTop = () => {
    document.querySelector('#searchResults').parentElement.scrollTop = 0
}

const searchLibrary = (query, filters={}) => {
    console.log(filters)
    const form = document.querySelector(`form[hx-get="${searchEndpoint}"]`)
    form.elements.query.value = query
    
    const event = new CustomEvent('submit')
    form.dispatchEvent(event)
}

document.addEventListener('htmx:configRequest', (event) => {
    const detail = event.detail
    if (detail.path === searchEndpoint && window.location.pathname === '/') {
        const requestParams = detail.parameters

        if (Object.keys(requestParams).length > 1){
            const urlParams = getURLParams()
            for (const key in urlParams) {
                if (!Object.keys(requestParams).includes(key)) {
                    requestParams[key] = urlParams[key]
                }
            }
        } else {
            removeURLParams()
        }

        pushParamsToURL(requestParams)
    }
})