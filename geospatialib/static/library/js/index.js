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