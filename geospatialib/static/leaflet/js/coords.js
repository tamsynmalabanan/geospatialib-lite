const loopThroughCoordinates = (coordinates, handler) => {
    if (Object.keys(coordinates).every(key => Array('lat', 'lng').includes(key))) {
        handler(coordinates)
    } else if (Array.isArray(coordinates) && coordinates.length === 2 && coordinates.every(item => typeof item === 'number')) {
        handler(coordinates)
    } else {
        Object.values(coordinates).forEach(value => loopThroughCoordinates(value, handler))
    }
    return coordinates
}

const validateCoordinates = (coords, precision=6) => {
    const reference = {
        'lat' : {min:-90, max:90},
        'lng' : {min:-180, max:180},
    }

    Object.keys(coords).forEach(dir => {
        const min = reference[dir].min
        const max = reference[dir].max
        
        let value = coords[dir]
        if (value < min) {
            value = min
        } else if (value > max) {
            value = max
        } else {
            value = Number(value.toFixed(precision))
        }
        
        coords[dir] = value
    })
}

const transformCoordinatesToEPSG4326 = (coordinates, crs_text) => {
    if (proj4.defs(crs_text)) {
        loopThroughCoordinates(coordinates, (coords) => {
            const projectedCoord = proj4(crs_text, 'EPSG:4326', [coords[0], coords[1]]);
            coords[0] = projectedCoord[0]
            coords[1] = projectedCoord[1]
        })

    } else {
        console.log('CRS definition is not on Proj4: ', crs_text)
    }

    return coordinates
}