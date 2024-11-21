const searchEndpoint = "/htmx/library/search/"

const resetSearchResults = () => {
    const searchResults = document.querySelector('#searchResults')
    if (searchResults) {
        searchResults.parentElement.scrollTop = 0
    }

    const map = mapQuerySelector('#geospatialibMap')
    if (map) {
        map.getLayerGroups().library.clearLayers()
    }
}

const searchLibrary = (query=null) => {
    const form = document.querySelector(`form[hx-get="${searchEndpoint}"]`)
    
    if (query !== null) {
        form.elements.query.value = query
    }
    
    const event = new CustomEvent('submit')
    form.dispatchEvent(event)
}

window.addEventListener("map:init", (event) => {
    const map = event.detail.map
    if (map.getContainer().id === 'geospatialibMap') {
        map.on('mapInitComplete', () => {
            const urlParams = getURLParams()
            const bbox = urlParams.bbox__bboverlaps
            if (bbox) {
                map.fitBounds(L.geoJSON(JSON.parse(bbox)).getBounds())
            }
        })
    }
})

document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'searchResults') {
        const map = mapQuerySelector('#geospatialibMap')
        map.fire('updateBboxFields')
    }
})

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