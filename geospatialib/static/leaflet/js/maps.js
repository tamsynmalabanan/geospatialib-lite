const mapQuerySelector = (selector) => {
    let map

    if (window.maps) {
        window.maps.forEach(currentMap => {
            if (currentMap.getContainer().matches(selector)) {
                map = currentMap
                return
            }
        })
    }

    return map
}

const clearAllLayers = (map) => {
    map.eachLayer(layer => {
        if (layer._url === "//tile.openstreetmap.org/{z}/{x}/{y}.png") {return}

        if (Object.values(map.getLayerGroups()).includes(layer)) {return}

        map.removeLayer(layer);
    });        
}

const getMeterScale = (map) => {
    let scale_value

    const scales = map.getContainer().querySelectorAll('.leaflet-control-scale-line')
    scales.forEach(scale => {
        const text = scale.innerText
        const lastChar = text.charAt(text.length - 1)
        if (lastChar === 'm') {
            const value = parseInt(text)
            if (text.includes('km')) {
                scale_value = value * 1000
            } else {
                scale_value = value
            }
            return
        }
    })

    return scale_value
}

const getMapBbox = (map) => {
    const bounds = loopThroughCoordinates(
        map.getBounds(), 
        validateCoordinates
    )
    
    return [
        bounds.getNorth(),
        bounds.getEast(),
        bounds.getSouth(),
        bounds.getWest(),
    ]
}

const disableLayerClick = (map) => {
    map.eachLayer(layer => {
        const clickFns = layer._events.click
        if (layer.off && clickFns) {
            layer.disabledClickFns = clickFns
            layer.off('click')
        }
    });
}

const enableLayerClick = (map) => {
    map.eachLayer(layer => {
        const clickFns = layer.disabledClickFns
        if (layer.on && clickFns) {
            layer._events.click = clickFns
            delete layer.disabledClickFns
        }
    });
}

const zoomMapToBbox = (map, bbox) => {
    if (typeof bbox === 'string') {
        bbox = bbox.replace('(', '[').replace(')', ']')
        bbox = JSON.parse(bbox)
    }

    const [minX, minY, maxX, maxY] = bbox
    const bounds = L.latLngBounds([[minY, minX], [maxY, maxX]]);
    map.fitBounds(bounds)

    return bounds
}