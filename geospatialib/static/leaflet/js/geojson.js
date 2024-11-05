const handleGeoJSON = (geojson, default_geom) => {
    handleFeatureId(geojson)
    handleGeoJSONGeometry(geojson, default_geom)
    sortGeoJSONFeatures(geojson)

    return geojson
}

const handleFeatureId = (geojson) => {
    geojson.features.forEach(feature => {
        if (feature.id) {
            feature.properties.feature_id = feature.id
        }
    })
}

const handleGeoJSONGeometry = (geojson, default_geom) => {
    let geom_assigned = false
    geojson.features.forEach(feature => {
        if (!feature.geometry) {
            feature.geometry = default_geom
            if (!geom_assigned) {geom_assigned = true}
        }
    })
    
    if (!geom_assigned && geojson.crs) {
        let crs
        const name = geojson.crs.properties.name
        if (name.includes('EPSG::')) {
            crs = parseInt(name.split('EPSG::')[1])
        }
    
        if (crs && crs !== 4326) {
            const crs_text = `EPSG:${crs}`
            if (!proj4.defs(crs_text)) {
                fetchProj4Def(crs, crs_text)
            }
    
            if (proj4.defs(crs_text)) {
                geojson.features.forEach(feature => {
                    const coords = feature.geometry.coordinates
                    transformCoordinatesToEPSG4326(coords, crs_text)
                })
            }
        }
    }

}

const sortGeoJSONFeatures = (geojson) => {
    geojson.features.sort((a, b) => {
        const featureTypeA = a.geometry.type;
        const featureTypeB = b.geometry.type;
    
        if (featureTypeA === 'Point' && featureTypeB !== 'Point') {
          return -1;
        } else if (featureTypeB === 'Point' && featureTypeA !== 'Point') {
          return 1;
        } else if (featureTypeA === 'MultiPoint' && featureTypeB !== 'MultiPoint') {
          return -1;
        } else if (featureTypeB === 'MultiPoint' && featureTypeA !== 'MultiPoint') {
          return 1;
        } else if (featureTypeA === 'LineString' && featureTypeB !== 'LineString') {
          return -1;
        } else if (featureTypeB === 'LineString' && featureTypeA !== 'LineString') {
          return 1;
        } else if (featureTypeA === 'MultiLineString' && featureTypeB !== 'MultiLineString') {
          return -1;
        } else if (featureTypeB === 'MultiLineString' && featureTypeA !== 'MultiLineString') {
          return 1;
        } else if (featureTypeA === 'Polygon' && featureTypeB !== 'Polygon') {
          return -1;
        } else if (featureTypeB === 'Polygon' && featureTypeA !== 'Polygon') {
          return 1;
        } else if (featureTypeA === 'MultiPolygon' && featureTypeB !== 'MultiPolygon') {
          return -1;
        } else if (featureTypeB === 'MultiPolygon' && featureTypeA !== 'MultiPolygon') {
          return 1;
        } else {
          return featureTypeA.localeCompare(featureTypeB);
        }
    });
}

const downloadGeoJSON = (geojson, file_name) => {
    const blob = new Blob([geojson], {type:'application/json'})
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${file_name}.geojson`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}