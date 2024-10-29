const toggleLibraryLayer = (event, mapSelector) => {
    const toggle = event.target
    const map = mapQuerySelector(mapSelector)
    if (map) {
        const data = toggle.dataset
        if (toggle.checked) {
            const layer = createLayerFromURL(data)
            if (layer) {
                map.getLayerGroups().client.addLayer(layer)
                toggle.setAttribute('data-layer-id', layer._leaflet_id)
            }
        } else {
            const id = data.layerId
            const layer = map.getLayerGroups().client.getLayer(id)
            if (layer) {
                map.removeLayer(layer)
            }
        }
    }
}

const createWMSLayer = (data) => {
    const url = new URL(data.layerUrl)
    const baseUrl = url.origin + url.pathname
    const options = {
        layers: data.layerName, 
        format: 'image/png',
        transparent: true,
    }

    if (data.layerStyles) {
        const styles = JSON.parse(data.layerStyles)
        options.styles = Object.keys(styles)[0]
    }
    
    return L.tileLayer.wms(baseUrl, options)
}

const createXYZTilesLayer = (data) => {
    return L.tileLayer(data.layerUrl)
}

const getCreateLayerHandler = (format) => {
    return {
        wms:createWMSLayer,
        xyz:createXYZTilesLayer,
    }[format]
}

const createLayerFromURL = (data) => {
    let layer

    const handler = getCreateLayerHandler(data.layerFormat)
    if (handler) {
        layer = handler(data)
    }
    
    if (layer) {
        layer.data = data

        if (data.layerBbox && !layer.hasOwnProperty('getBounds')) {
            const geojson = JSON.parse(data.layerBbox)
            const bbox = L.geoJSON(geojson)
            const bounds = bbox.getBounds()
            layer.getBounds = () => {
                if (bounds) {
                    return bounds
                }
            }

        }
    }
    
    return layer
}

const getLayerLoadEvents = (format) => {
    return {
        wms: {load: 'tileload', error: 'tileerror'},
        xyz: {load: 'tileload', error: 'tileerror'},
    }[format]
}

const assignLayerLoadEventHandlers = (layer, onload=null, onerror=null) => {
    const e = getLayerLoadEvents(layer.data.layerFormat)

    if (onload) {
        const onLoadHandler = (event) => {
            onload(event);
            layer.removeEventListener(e.load, onLoadHandler)
            if (onerror) {
                layer.removeEventListener(e.error, onerror)
            }
        }

        layer.addEventListener(e.load, onLoadHandler)
    }

    if (onerror) {
        layer.addEventListener(e.error, onerror)
    }
};
