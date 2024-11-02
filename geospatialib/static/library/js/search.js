const searchEndpoint = "/htmx/library/search/"

const searchResultsScrollTop = () => {
    document.querySelector('#searchResults').parentElement.scrollTop = 0
}

const searchLibrary = (query=null) => {
    const form = document.querySelector(`form[hx-get="${searchEndpoint}"]`)
    
    if (query !== null) {
        form.elements.query.value = query
    }
    
    const event = new CustomEvent('submit')
    form.dispatchEvent(event)
}

const assignBboxFilterValue = (map) => {
    const bboxFilter = document.querySelector('[name="bbox__bboverlaps"]')
    if (bboxFilter) {
        const bounds = loopThroughCoordinates(map.getBounds(), validateCoordinates)
        const geom = JSON.stringify(L.rectangle(bounds).toGeoJSON().geometry)
        bboxFilter.value = geom
    }
}

let bboxFilterTimeout
window.addEventListener("map:init", (event) => {
    const map = event.detail.map
    if (map.getContainer().id === 'geospatialibMap') {
        map.getContainer().addEventListener('mapInitComplete', () => {
            const urlParams = getURLParams()
            const bbox = urlParams.bbox__bboverlaps
            if (bbox) {
                map.fitBounds(L.geoJSON(JSON.parse(bbox)).getBounds())
            }
    
            assignBboxFilterValue(map)
            map.on('resize moveend zoomend', (event) => {
                clearTimeout(bboxFilterTimeout);
                bboxFilterTimeout = setTimeout(() => {
                    assignBboxFilterValue(map)
                }, 100)
            })
        })
    }
})

document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.id === 'searchResults') {
        const map = mapQuerySelector('#geospatialibMap')
        assignBboxFilterValue(map)
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
