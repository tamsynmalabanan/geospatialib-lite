const mapQuerySelector = (selector) => {
    let map

    window.maps.forEach(currentMap => {
        if (currentMap.getContainer().matches(selector)) {
            map = currentMap
            return
        }
    })

    return map
}

const clearAllLayers = (map) => {
    map.eachLayer(layer => {
        if (layer._url === "//tile.openstreetmap.org/{z}/{x}/{y}.png") {return}

        if (Object.values(map.getLayerGroups()).includes(layer)) {return}

        map.removeLayer(layer);
    });        
}

const getScale = (map, unit='km') => {
    let scale_value

    const scales = map.getContainer().querySelectorAll('.leaflet-control-scale-line')
    scales.forEach(scale => {
        if (scale.innerText.includes(unit)) {
            scale_value = parseInt(scale.innerText)
            return
        }
    })

    return scale_value
}