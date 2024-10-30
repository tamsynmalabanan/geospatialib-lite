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