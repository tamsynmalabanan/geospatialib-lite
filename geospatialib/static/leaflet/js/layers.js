const populateLayerDropdownMenu = (toggle, options={}) => {
    const dropdown = toggle.nextElementSibling
    if (dropdown && dropdown.innerHTML.trim() === '') {
        let map = options.map
        if (!map && options.mapSelector) {
            map = mapQuerySelector(options.mapSelector)
        }

        const layerList = toggle.closest('ul')
        if (map && layerList) {
            const toggleAll = document.querySelector(`[data-layers-toggles="#${layerList.id}"]`)
            let label = toggleAll.getAttribute('data-layers-label')
            if (!label) {
                label = 'layer'
            }

            let bounds = options.bounds
            if (!bounds ) {
                if (options.bboxCoords) {
                    const [minX, minY, maxX, maxY] = options.bboxCoords.slice(1, -1).split(',')
                    bounds = L.latLngBounds([[minY, minX], [maxY, maxX]]);
                } else if (options.layer) {
                    const layer = options.layer
                    bounds = getLayerBounds(layer)              
                }
            }
    
            if (bounds) {
                const zoomBtn = createDropdownMenuListItem({
                    label: `Zoom to ${label}`,
                    buttonClass: 'bi bi-zoom-in',
                })
                dropdown.appendChild(zoomBtn)
                zoomBtn.addEventListener('click', () => {
                    if (bounds.getNorth() === bounds.getSouth() && bounds.getEast() === bounds.getWest()) {
                        map.setView(bounds.getNorthEast(), 15)
                    } else {
                        map.fitBounds(bounds)
                    }
                })
            }

            const isolateBtn = createDropdownMenuListItem({
                label: `Isolate ${label}`,
                buttonClass: 'bi bi-subtract',
            })
            dropdown.appendChild(isolateBtn)
            isolateBtn.addEventListener('click', () => {
                const checkbox = findOuterElement('input.form-check-input', toggle)
                if (checkbox) {
                    layerList.querySelectorAll('input').forEach(input => {
                        if (input.checked && input !== checkbox) {
                            input.click()
                        }
                    })

                    if (!checkbox.checked) {
                        checkbox.click()
                    }
                }
            })

            let geojson = options.geojson
            if (!geojson && options.layer) {
                geojson = options.layer.toGeoJSON()
            }

            if (geojson) {
                let filename
                if (options.layer) {
                    filename = options.layer.title
                } else {
                    filename = 'geojson'
                }

                const downloadBtn = createDropdownMenuListItem({
                    label: `Download geojson`,
                    buttonClass: 'bi bi-download',
                })
                dropdown.appendChild(downloadBtn)
                downloadBtn.addEventListener('click', () => {
                    let geojson_str = geojson
                    if (typeof geojson === 'object') {
                        geojson_str = JSON.stringify(geojson)
                    }
        
                    downloadGeoJSON(geojson_str, filename)
                })
            }
        }
    }
}

const toggleOffAllLayers = (toggle) => {
    const targetSelector = toggle.getAttribute('data-layers-toggles')
    const target = document.querySelector(targetSelector)
    if (target) {
        const toggles = target.querySelectorAll('input[type="checkbox"]')
        toggles.forEach(toggle => {
            if (toggle.checked) {
                toggle.click()
            }
        })
    }
    toggle.setAttribute('disabled', true)
}

const toggleLayer = async (event, options={}) => {
    let map = options.map
    if (!map && options.mapSelector) {
        map = mapQuerySelector(options.mapSelector)
    }

    if (map) {
        const toggle = event.target
        
        let toggleAll
        let toggleLabel
        const layerList = toggle.closest('ul')
        if (layerList) {
            toggleAll = document.querySelector(`input[data-layers-toggles="#${layerList.id}"]`)
            toggleLabel = document.querySelector(`label[for="${toggleAll.id}"]`)
        }

        let layerGroup = map.getLayerGroups()[options.layerGroup]
        if (!layerGroup) {
            layerGroup = map.getLayerGroups().library
        }
        
        const data = toggle.dataset
        if (toggle.checked) {
            let layer = options.layer
            if (!layer && data) {
                layer = createLayerFromURL(data)
            }

            if (layer) {
                layerGroup.addLayer(layer)
                toggle.setAttribute('data-leaflet-id', layer._leaflet_id)
            }
        } else {
            const layer = layerGroup.getLayer(data.leafletId)
            if (layer) {
                layerGroup.removeLayer(layer)
            }
        }

        if (toggleAll) {
            const layersCount = layerGroup.getLayers().length
            if (layersCount < 1) {
                toggleAll.setAttribute('disabled', true)
                toggleAll.checked = false

                toggleLabel.innerHTML = ''
            } else {
                toggleAll.removeAttribute('disabled')
                toggleAll.checked = true

                let label = toggleAll.getAttribute('data-layers-label')
                if (!label) {
                    label = 'layer'
                }

                if (layersCount > 1) {
                    toggleLabel.innerHTML = `showing ${layersCount} ${label}s`
                } else {
                    toggleLabel.innerHTML = `showing ${layersCount} ${label}`
                }
            }
        }
    }
}

const getLayerTitle = (layer) => {
    let title

    if (layer.feature && layer.feature.properties) {
        const properties = layer.feature.properties
        title = properties['display_name']

        if (!title) {
            title = searchByObjectPropertyKeyword(properties, 'name')
        }

        if (!title) {
            title = searchByObjectPropertyKeyword(properties, 'feature_id')
        }
        
        if (!title) {
            title = properties['type']
        }
        
        if (!title) {
            for (const key in properties) {
                const value = properties[key]
                if (typeof value === 'string' && value.length < 50) {
                    title = `${key}: ${value}`
                    return title
                }
            }
        }
    }

    return title
}

const createFeaturePropertiesTable = (properties) => {
    const table = document.createElement('table')
    table.classList.add('table', 'table-striped', 'fs-12')
    
    const tbody = document.createElement('tbody')
    table.appendChild(tbody)
    
    const handler = (properties) => {
        Object.keys(properties).forEach(property => {
            let data = properties[property]
            
            if (data && typeof data === 'object') {
                handler(data)
            } else {
                if (!data) {data = null}

                const tr = document.createElement('tr')
                tbody.appendChild(tr)
                
                const th = document.createElement('th')
                th.innerText = property
                th.setAttribute('scope', 'row')
                tr.appendChild(th)
        
                const td = document.createElement('td')

                td.innerHTML = data
                tr.appendChild(td)
            }
        })
    }

    handler(properties)

    return table
}

const getLayerBounds = (layer) => {
    try {
        return layer.getBounds()
    } catch {
        return L.latLngBounds(layer.getLatLng(), layer.getLatLng())
    }
}

const createLayerToggles = (layer, parent, map, layerGroup, geojson) => {
    const mapContainer = map.getContainer()

    let label = layer.title
    let layerCount = 0
    if (layer._layers) {
        layerCount = layer.getLayers().length
        if (layerCount > 1) {
            label = `${layer.title} (${formatNumberWithCommas(layerCount)} features)`
        }
    }

    const handler = (layer, parent, geojson, label) => {
        const formCheck = createFormCheck(`${mapContainer.id}_${layer._leaflet_id}`, {
            formCheckClass: 'fw-medium',
            label: label,
            parent: parent,
            button: true,
            buttonClass: 'bi bi-three-dots',
            buttonAttrs: {
                'data-bs-toggle': 'dropdown',
                'aria-expanded': 'false',
            }
        })

        const dropdown = document.createElement('ul')
        dropdown.className = 'dropdown-menu fs-12'
        formCheck.appendChild(dropdown)

        const toggle = formCheck.querySelector('button')
        toggle.addEventListener('click', () => {
            populateLayerDropdownMenu(toggle, {
                map: map,
                layer: layer,
                layerGroup: layerGroup,
                geojson: geojson,
            })
        })

        if (layer.feature && layer.feature.properties) {
            const properties = layer.feature.properties
            if (Object.keys(properties).length > 0) {
                const collapse = document.createElement('div')
                collapse.id = `${mapContainer.id}_${layer._leaflet_id}_properties`
                collapse.className = 'collapse px-4'
                parent.appendChild(collapse)

                const table = createFeaturePropertiesTable(properties)
                collapse.appendChild(table)

                const collapseToggle = document.createElement('button')
                collapseToggle.className = 'dropdown-toggle bg-transparent border-0 ps-2 pe-0'
                collapseToggle.setAttribute('type', 'button')
                collapseToggle.setAttribute('data-bs-toggle', 'collapse')
                collapseToggle.setAttribute('data-bs-target', `#${collapse.id}`)
                collapseToggle.setAttribute('aria-controls', collapse.id)
                collapseToggle.setAttribute('aria-expanded', `false`)
                formCheck.appendChild(collapseToggle)        
            }
        }

        return formCheck
    }
    
    const mainToggle = handler(layer, parent, geojson, label)
    const mainCheckbox = mainToggle.querySelector('input')

    if (layerCount > 0 && layerCount <= 100) {
        const collapse = document.createElement('div')
        collapse.id = `${mapContainer.id}_${layer._leaflet_id}_group`
        collapse.className = 'collapse show ps-3'
        parent.appendChild(collapse)

        const collapseToggle = document.createElement('button')
        collapseToggle.className = 'dropdown-toggle bg-transparent border-0 ps-2 pe-0'
        collapseToggle.setAttribute('type', 'button')
        collapseToggle.setAttribute('data-bs-toggle', 'collapse')
        collapseToggle.setAttribute('data-bs-target', `#${collapse.id}`)
        collapseToggle.setAttribute('aria-controls', collapse.id)
        collapseToggle.setAttribute('aria-expanded', `true`)
        mainToggle.appendChild(collapseToggle)

        mainCheckbox.addEventListener('click', async (event) => {
            if (mainCheckbox.checked) {
                collapse.querySelectorAll('input').forEach(checkbox => {
                    if (!checkbox.checked) {
                        checkbox.click()
                    }
                })
            } else {
                collapse.querySelectorAll('input').forEach(checkbox => {
                    if (checkbox.checked) {
                        checkbox.click()
                    }
                })
            }
        })

        map.on('layeradd', (event) => {
            if (layer.hasLayer(event.layer)) {
                if (layer.getLayers().every(feature => map.hasLayer(feature))) {
                    mainCheckbox.removeAttribute('disabled')
                    mainCheckbox.checked = true
                }
            }
        })

        map.on('layerremove', (event) => {
            if (layer.hasLayer(event.layer)) {
                mainCheckbox.checked = false
            }
        })

        layer.eachLayer(feature => {
            const layerToggle = handler(feature, collapse, feature.feature, feature.title)
            const layerCheckbox = layerToggle.querySelector('input')
            layerCheckbox.addEventListener('click', (event) => {
                toggleLayer(event, {
                    map: map,
                    layer: feature,
                    layerGroup: layerGroup,
                })
            })    
        })

        return [mainToggle, collapse]
    } else {
        if (layerCount > 1000) {
            mainCheckbox.setAttribute('disabled',true)
        } else {
            mainCheckbox.addEventListener('click', (event) => {
                toggleLayer(event, {
                    map: map,
                    layer: layer,
                    layerGroup: layerGroup,
                })
            })    
        }

        mainToggle.classList.add('pe-3')

        return [mainToggle, undefined]
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

    return L.tileLayer.wms(baseUrl, options)
}

const createWFSLayer = (data) => {
    const color = `hsla(${Math.floor(Math.random() * 361)}, 100%, 50%, 1)`

    const geojsonLayer = L.geoJSON({type: "FeatureCollection", features: []}, {
        pointToLayer: (geoJsonPoint, latlng) => {
            return L.marker(latlng, {icon:getDefaultLayerStyle('point', {color:color})})
        },
        style: (geoJsonFeature) => {
            return getDefaultLayerStyle('other', {color:color})
        },
        onEachFeature: (feature, layer) => {
            if (Object.keys(feature.properties).length > 0) {
                layer.bindPopup(createFeaturePropertiesTable(feature.properties).outerHTML, {
                    autoPan: false,
                })

                layer.on('popupopen', (event) => {
                    const map = layer._map
                    const wrapper = event.popup._container.querySelector('.leaflet-popup-content-wrapper')
                    wrapper.classList.add(`text-bg-${getPreferredTheme()}`, 'overflow-auto')
                    wrapper.style.maxHeight = `${map.getSize().y * 0.5}px`
                    event.popup._container.querySelector('.leaflet-popup-tip').classList.add(`bg-${getPreferredTheme()}`)
                })
            }
        }
    })

    geojsonLayer.data = data
    geojsonLayer.data.layerLegendObj = '{}'
    
    geojsonLayer.on('add', (event) => {
        const map = event.target._map

        const fetchData = () => {
            fetchWFSData(event, geojsonLayer)
            .then(geojson => {
                let prefix
                let suffix

                if (geojson) {
                    const mapScale = getMeterScale(map)
                    const featureCount = geojson.features.length
    
                    if (mapScale > 10000) {
                        if (featureCount > 1000) {
                            geojson.features = [turf.bboxPolygon(turf.bbox(geojson))]
                            prefix = 'Bounding'
                            suffix = `(${formatNumberWithCommas(featureCount)} features)`
                        } else {
                            geojson = turf.simplify(geojson, { tolerance: 0.01 })
                            prefix = 'Simplified'
                        }
                    }    
                } else {
                    if (geojsonLayer.data && geojsonLayer.data.layerBbox) {
                        geojson = {
                            type: 'FeatureCollection',
                            features: [turf.bboxPolygon(geojsonLayer.data.layerBbox.slice(1, -1).split(','))]
                        }
        
                        prefix = 'Bounding'
                        suffix = '(all features)'
                    }
                }

                if (geojson) {
                    geojson = handleGeoJSON(geojson)

                    geojsonLayer.clearLayers()
                    geojsonLayer.addData(geojson)
                    
                    let legend = {}
                    geojsonLayer.eachLayer(feature => {
                        const type = feature.feature.geometry.type.replace('Multi', '')
                        
                        let label
                        if (type === 'Point') {
                            label = type
                        } else {
                            label = Array(prefix, type, suffix).filter(part => part).join(' ')
                        }

                        if (!Object.keys(legend).includes(label)) {
                            let style
                            if (type === 'Point') {
                                style = geojsonLayer.options.pointToLayer().options.icon
                            } else {
                                style = geojsonLayer.options.style()
                            }

                            legend[label] = {
                                type: type,
                                style: style
                            }
                        }
                    })
    
                    geojsonLayer.data.layerLegendObj = JSON.stringify(legend)
                    geojsonLayer.fire('legend_updated')
                }
            })
        }

        let fetchWFSDataTimeout
        const fetchDataOnTimeout = () => {
            clearTimeout(fetchWFSDataTimeout)
            fetchWFSDataTimeout = setTimeout(fetchData, 1000)
        }

        fetchData()
        map.on('moveend zoomend', fetchDataOnTimeout)
        geojsonLayer.on('remove', () => {
            map.off('moveend', fetchDataOnTimeout)
        })
    })

    return geojsonLayer
}

const createXYZTilesLayer = (data) => {
    return L.tileLayer(data.layerUrl)
}

const getCreateLayerHandler = (format) => {
    return {
        wms:createWMSLayer,
        wfs:createWFSLayer,
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
        wfs: {load: 'fetched', error: 'error'},
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
}

const isMultiPointLayer = (layer) => {
    return layer.feature && layer.feature.geometry.type === 'MultiPoint'
}

const isPointLayer = (layer) => {
    return layer._latlng || isMultiPointLayer(layer)
}

const getDefaultLayerStyle = (type, options={}) => {
    let color = options.color
    if (!color) {
        color = 'hsla(0, 100%, 50%, 1)'
    }

    let strokeWidth = options.strokeWidth
    let weight = options.weight

    if (!strokeWidth) {
        if (weight) {
            strokeWidth = weight
        } else {
            strokeWidth = 1
        }
    }

    if (!weight) {
        weight = strokeWidth
    }

    if (type.toLowerCase() === 'point') {
        let strokeColor = options.strokeColor
        if (!strokeColor) {
            if (color.startsWith('hsla')) {
                [h,s,l,a] = color.split(',').map(str => parseNumberFromString(str))
                l = l / 2
                strokeColor = `hsla(${h}, ${s}%, ${l}%, ${a})`
            } else {
                strokeColor = 'grey'
            }
        }

        const div = document.createElement('div')
        div.className = 'h-100 w-100 rounded-circle'
        div.style.backgroundColor = color
        div.style.border = `${strokeWidth}px solid ${strokeColor}`

        return L.divIcon({
            className: 'bg-transparent',
            html: div.outerHTML,
        });
    } else {
        let opacity = options.opacity
        if (!opacity) {
            opacity = 1
        }

        const properties = {
            color: color,
            weight: weight,
            opacity: opacity
        }

        let fillColor = options.fillColor
        if (fillColor) {
            if (typeof fillColor === 'boolean') {
                if (color.startsWith('hsla')) {
                    [h,s,l,a] = color.split(',').map(str => parseNumberFromString(str))
                    l = (l / 2 * 3)
                    fillColor = `hsla(${h}, ${s}%, ${l > 100 ? 100 : l}%, ${a})`
                } else {
                    fillColor = white
                }
            }

            let fillOpacity = options.fillOpacity
            if (!fillOpacity) {
                fillOpacity = 0.25
            }
                
            properties.fillOpacity = fillOpacity
            properties.fillColor = fillColor
        } else {
            properties.fillOpacity = 0
        }

        return properties
    }
}

const assignDefaultLayerStyle = (layer, options={}) => {
    let style

    if (isPointLayer(layer)) {
        style = getDefaultLayerStyle('point', options)
        if (isMultiPointLayer(layer)) {
            layer.eachLayer(i => i.setIcon(style))
        } else {
            layer.setIcon(style)
        }
    } else {
        style = getDefaultLayerStyle('other', options)
        layer.setStyle(style)
    }

    return style
}