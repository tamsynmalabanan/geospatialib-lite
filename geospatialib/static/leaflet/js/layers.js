const populateLayerDropdownMenu = (toggle, coords, mapSelector) => {
    const dropdown = toggle.nextElementSibling
    if (dropdown && dropdown.innerHTML.trim() === '') {
        const map = mapQuerySelector(mapSelector)
        const layerList = toggle.closest('ul')
        if (layerList) {
            if (map) {
                const [minX, minY, maxX, maxY] = coords.slice(1, -1).split(',')
                const bounds = L.latLngBounds([[minY, minX], [maxY, maxX]]);
                if (bounds) {
                    const item = createDropdownMenuListItem('Zoom to layer')
                    item.addEventListener('click', () => {
                        map.fitBounds(bounds)
                    })
                    dropdown.appendChild(item)
                }
            }
        }
    }
}

const toggleOffAllLayers = (toggle) => {
    const targetSelector = toggle.getAttribute('data-layer-toggles')
    const target = document.querySelector(targetSelector)
    if (target) {
        const toggles = target.querySelectorAll('input[type="checkbox"]')
        toggles.forEach(toggle => {
            if (toggle.checked) {
                toggle.click()
            }
        })
    }
}

const toggleLibraryLayer = (event, mapSelector) => {
    const map = mapQuerySelector(mapSelector)
    if (map) {
        const toggle = event.target
        
        let toggleAll
        let toggleLabel
        let layersCount
        const layerList = toggle.closest('ul')
        if (layerList) {
            toggleAll = document.querySelector(`input[data-layer-toggles="#${layerList.id}"]`)
            toggleLabel = document.querySelector(`label[for="${toggleAll.id}"]`)
        }
        
        const data = toggle.dataset
        if (toggle.checked) {
            const layer = createLayerFromURL(data)
            if (layer) {
                map.getLayerGroups().search.addLayer(layer)
                toggle.setAttribute('data-leaflet-id', layer._leaflet_id)

                if (toggleAll) {
                    layersCount = parseInt(toggleAll.getAttribute('data-layers-shown'))+1
                }
            }
        } else {
            const layer = map.getLayerGroups().search.getLayer(data.leafletId)
            if (layer) {
                map.removeLayer(layer)

                if (toggleAll) {
                    layersCount = parseInt(toggleAll.getAttribute('data-layers-shown'))-1
                }
            }
        }

        if (toggleAll) {
            toggleAll.setAttribute('data-layers-shown', layersCount)
            
            if (layersCount < 1) {
                toggleAll.setAttribute('disabled', true)
                toggleAll.checked = false

                toggleLabel.innerHTML = ''
            } else {
                toggleAll.removeAttribute('disabled')
                toggleAll.checked = true

                if (layersCount > 1) {
                    toggleLabel.innerHTML = `showing ${layersCount} layers`
                } else {
                    toggleLabel.innerHTML = `showing ${layersCount} layer`
                }
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
            const [minX, minY, maxX, maxY] = data.layerBbox.slice(1, -1).split(',')
            const bounds = L.latLngBounds([[minY, minX], [maxY, maxX]]);
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
