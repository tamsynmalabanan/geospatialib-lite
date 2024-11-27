let geospatialibMap

const handleMapFocusAreaBbox = (bbox) => {
    const handler = () => {
        const bounds = zoomMapToBbox(geospatialibMap, bbox)
        geospatialibMap.resetviewControl.getBounds = () => bounds
    }

    if (geospatialibMap && geospatialibMap.initComplete === true) {
        handler()
    } else {
        window.addEventListener("map:init", (event) => {
            const map = event.detail.map
            if (map.getContainer().id === 'geospatialibMap') {
                geospatialibMap = map
                map.on('mapInitComplete', () => {
                    handler()
                })
            }
        })
    }
}
