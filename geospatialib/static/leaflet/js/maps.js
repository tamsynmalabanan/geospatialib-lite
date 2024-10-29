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

// const zoomToGeoJSON = (mapSelector, geojson) => {
//     const map = mapQuerySelector(mapSelector)
//     if (map) {
//         if (typeof geojson === 'string') {
//             geojson = JSON.parse(geojson)
//         }

//         const layer = L.geoJSON(geojson)
//         map.fitBounds(layer.getBounds())
//     }
// }

const clearAllLayers = (map) => {
    map.eachLayer(layer => {
        if (layer._url === "//tile.openstreetmap.org/{z}/{x}/{y}.png") {return}

        if (Object.values(map.getLayerGroups()).includes(layer)) {return}

        map.removeLayer(layer);
    });        
}