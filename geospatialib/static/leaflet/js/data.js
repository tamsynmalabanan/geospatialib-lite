const fetchProj4Def = async (crs_int, crs_text) => {
    return fetchDataWithTimeout(`https://spatialreference.org/ref/epsg/${crs_int}/proj4.txt`)
    .then(response => {
        if (response.ok || response.status === 200) {
            return response.text()
        } else {
            throw new Error('Response not ok')
        }
    })
    .then(def => {
        proj4.defs(crs_text, def)
        return proj4.defs(crs_text)
    })
    .catch(error => console.log(error))
}

const fetchOSMData = async (event) => {
    const data = await Promise.all([
        fetchOSMDataAroundLatLng(event.latlng),
        fetchOSMDataFromNominatim(event),
    ])

    let features = []
    data.forEach(geojson => {
        if (geojson) {
            features = features.concat(geojson.features)
        }
    })

    const geojson = {
        type: "FeatureCollection",
        licence: "Data © <a href='http://osm.org/copyright' target='_blank'>OpenStreetMap contributors, ODbL 1.0.</a>",
        features: features
    }

    return handleGeoJSON(geojson)
}

const fetchOSMDataInBbox = async (bbox) => {
    return fetchDataWithTimeout("http://overpass-api.de/api/interpreter", 5000, {
        method: "POST",
        body: "data="+ encodeURIComponent(`
            [bbox:${bbox[0]},${bbox[1]},${bbox[2]},${bbox[3]}]
            [out:json]
            [timeout:180]
            ;
            (
                node
                    (
                        ${bbox[2]},
                        ${bbox[3]},
                        ${bbox[0]},
                        ${bbox[1]}
                    );
                way
                    (
                        ${bbox[2]},
                        ${bbox[3]},
                        ${bbox[0]},
                        ${bbox[1]}
                    );
                relation
                    (
                        ${bbox[2]},
                        ${bbox[3]},
                        ${bbox[0]},
                        ${bbox[1]}
                    );
            );
            out geom;
        `)
    }).then(response => {
        if (response.ok || response.status === 200) {
            return response.json()
        } else {
            throw new Error('Response not ok')
        }
    })
    .then(data => {
        const filteredElements = data.elements.filter(element => Object.keys(element).includes('tags'))
        data.elements = filteredElements
        return {
            type: "FeatureCollection",
            features:overpassOSMDataToGeoJSON(data)
        }
    })
    .catch(error => {
        console.error(error)
        return
    })
}

const fetchOSMDataAroundLatLng = async (latlng) => {

    const fetchData = async (buffer=10, minimum=1) => {
        const params = `around:${buffer},${latlng.lat},${latlng.lng}`
        return fetchDataWithTimeout("http://overpass-api.de/api/interpreter", 5000, {
            method: "POST",
            body: "data="+ encodeURIComponent(`
                [out:json][timeout:180];
                (
                    node(${params});
                    way(${params});
                    relation(${params});
                );
                out tags geom body;
            `)
        }).then(response => {
            if (response.ok || response.status === 200) {
                return response.json()
            } else {
                throw new Error('Response not ok')
            }
        }).then(data => {
            if (data && data.elements) {
                const newElements = data.elements.filter(element => Object.keys(element).includes('tags'))
                if ((newElements.length >= minimum) || buffer > 100000) {
                    data.elements = newElements
                    return data
                } else {
                    return fetchData(buffer*2, minimum*1.25)                    
                }
            } else {
                throw new Error('No elements returned.')
            }
        }).catch(error => {
            return
        })
    }

    const data = await fetchData()
    return {
        type: "FeatureCollection",
        features:overpassOSMDataToGeoJSON(data)
    }
}

const overpassOSMDataToGeoJSON = (data) => {
    let features = []
    
    if (data && data.elements && data.elements.length > 0) {
        let index = data.elements.length
        // while (features.length < 100 && index >= 0) {
        while (index > 0) {
            index -=1
            
            const element = data.elements[index]
            const type = element.type
            const tags = element.tags   

            const geojson = {type: "Feature", properties:tags}
            geojson.properties.osm_id = element.id
            geojson.properties.osm_type = type
            geojson.properties.osm_api = data.generator
            
            if (type === 'relation') {
                const points = []
                const polygons = []
                const linestrings = []
                element.members.forEach(member => {
                    const memberType = member.type
                    if (memberType === 'node') {
                        points.push(member)
                    } else {
                        if (member.geometry) {
                            const firstCoords = member.geometry[0]
                            const lastCoords = member.geometry[member.geometry.length-1]
                            if (firstCoords.lat === lastCoords.lat && firstCoords.lon === lastCoords.lon) {
                                polygons.push(member)
                            } else {
                                linestrings.push(member)
                            }
                        }
                    }
                })

                if (points.length !== 0) {
                    const geojson_mpt = Object.assign({}, geojson);
                    geojson_mpt.geometry = {
                        type: 'MultiPoint',
                        coordinates: []
                    }

                    points.forEach(point => {
                        geojson_mpt.geometry.coordinates.push([parseFloat(point.lon), parseFloat(point.lat)])
                    })

                    features.push(geojson_mpt)
                }

                if (linestrings.length !== 0) {
                    const geojson_mls = Object.assign({}, geojson);
                    geojson_mls.geometry = {
                        type: 'MultiLineString',
                        coordinates: []
                    }
                    
                    linestrings.forEach(line => {
                        const lineGeom = []
                        line.geometry.forEach(coords => lineGeom.push([parseFloat(coords.lon), parseFloat(coords.lat)]))
                        geojson_mls.geometry.coordinates.push(lineGeom)
                    })

                    features.push(geojson_mls)
                }

                if (polygons.length !== 0) {
                    const geojson_mp = Object.assign({}, geojson);
                    geojson_mp.geometry = {
                        type: 'MultiPolygon',
                        coordinates: []
                    }
                    
                    const outerGeoms = []
                    const innerGeoms = []
                    polygons.forEach(polygon => {
                        const polygonGeom = []
                        polygon.geometry.forEach(coords => polygonGeom.push([parseFloat(coords.lon), parseFloat(coords.lat)]))
                        if (polygon.role === 'inner') {
                            innerGeoms.push(polygonGeom)
                        } else {
                            outerGeoms.push(polygonGeom)
                        }
                    })
                    geojson_mp.geometry.coordinates.push(outerGeoms)
                    geojson_mp.geometry.coordinates.push(innerGeoms)

                    features.push(geojson_mp)
                }

            } else {
                if (type === 'node') {
                    geojson.geometry = {
                        type: 'Point',
                        coordinates: [parseFloat(element.lon), parseFloat(element.lat)]
                    }
                }

                if (type === 'way') {
                    const firstCoords = element.geometry[0]
                    const lastCoords = element.geometry[element.geometry.length-1]
                    let featureType = 'LineString'
                    if (firstCoords.lat === lastCoords.lat && firstCoords.lon === lastCoords.lon) {
                        featureType = 'Polygon'
                    }

                    geojson.geometry = {
                        type: featureType,
                        coordinates: []
                    }

                    element.geometry.forEach(coords => {
                        geojson.geometry.coordinates.push([parseFloat(coords.lon), parseFloat(coords.lat)])
                    })

                    if (featureType === 'Polygon') {
                        geojson.geometry.coordinates = [geojson.geometry.coordinates]
                    }
                }

                features.push(geojson)
            }
        }
    }

    return features
}

const fetchOSMDataFromNominatim = async (event) => {
    const getZoom = () => {
        const map = event.target
        
        let zoom = map.getZoom()
        if (zoom > 18) {
            zoom = 18
        }
        
        return zoom
    }

    const url = 'https://nominatim.openstreetmap.org/reverse?'
    return fetchDataWithTimeout(pushQueryParamsToURLString(url, {
            lat: event.latlng.lat,
            lon: event.latlng.lng,
            zoom: getZoom(),
            format: 'geojson',
            polygon_geojson: 1,
            polygon_threshold: 0,
        }
    )).then(response => {
        if (response.ok || response.status === 200) {
            return response.json()
        } else {
            throw new Error('Response not ok')
        }
    }).then(data => {
        if (data && data.features && data.features.length > 0) {
            const features = data.features
            features.forEach(feature => {
                feature.properties.osm_api = url
            })
            return data
        } else {
            throw new Error('No features returned.')
        }
    }).catch(error => {
        return
    });
}

const fetchData = (event, layer) => {
    return {
        wms: fetchWMSData,
    }[layer.data.layerFormat](event, layer)
}

const fetchWMSData = async (event, layer) => {
    const map = event.target
    const cleanURL = removeQueryParams(layer.data.layerUrl)
    const params = {
        SERVICE: 'WMS',
        VERSION: '1.1.1',
        REQUEST: 'GetFeatureInfo',
        SRS: "EPSG:4326",
        FORMAT: 'application/json',
        TRANSPARENT: true,
        QUERY_LAYERS: layer.data.layerName,
        LAYERS: layer.data.layerName,
        exceptions: 'application/vnd.ogc.se_inimage',
        INFO_FORMAT: 'application/json',
        X: Math.floor(event.containerPoint.x),
        Y: Math.floor(event.containerPoint.y),
        CRS: 'EPSG:4326',
        WIDTH: Math.floor(map.getSize().x),
        HEIGHT: Math.floor(map.getSize().y),
        BBOX: map.getBounds().toBBoxString(),
    }

    if (layer.data.layerStyles) {
        const styles = JSON.parse(layer.data.layerStyles)
        params.STYLES = Object.keys(styles)[0]
    }

    const url = pushQueryParamsToURLString(cleanURL, params)
    return fetchDataWithTimeout(url).then(response => {
        if (response.ok || response.status === 200) {
            return response.json()
        } else {
            throw new Error('Response not ok')
        }
    }).then(data => {
        if (data && data.features && data.features.length > 0) {
            data.licence = `Data © <a href='${cleanURL}' target='_blank'>${getDomain(cleanURL)}</a>`
            return handleGeoJSON(data)
        } else {
            throw new Error('No features returned.')
        }
    }).catch(error => {
        return
    })
}