const fetchOSMData = async (bbox) => {
    return fetch("https://overpass-api.de/api/interpreter", {
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
    }).then(data => {
        return data.json()
    })
}

const fetchData = (map, layer, bbox) => {
    return {
        wms: fetchWMSData,
    }[layer.data.layerFormat](map, layer, bbox)
}

const fetchWMSData = async (map, layer, bbox) => {
    const cleanURL = layer.data.layerUrl.split('?')[0]
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
        Y: Math.floor(mapClickEvent.containerPoint.y),
        CRS: 'EPSG:4326',
        WIDTH: Math.floor(map.getSize().x),
        HEIGHT: Math.floor(map.getSize().y),
        BBOX: map.getBounds().toBBoxString(),
    }

    if (layer.data.legendname) {
        params.STYLES = layer.data.legendname
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    return fetch(pushQueryParamsToURLString(layer._url, params), {
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId)
        if (response.ok || response.status === 200) {
            return response.json()
        } else {
            throw new Error('Response not ok')
        }
    })
    .then(data => {
        if (data && data.features && data.features.length !== 0) {
            return data
        } else {
            throw new Error(`No features returned from ${layer.data.legendtitle}`)
        }
    })
}