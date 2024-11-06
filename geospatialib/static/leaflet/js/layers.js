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
                    try {
                        bounds = layer.getBounds()
                    } catch {
                        bounds = L.latLngBounds(layer.getLatLng(), layer.getLatLng())
                    }                
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
                        map.setView(bounds.getNorthEast(), 10)
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

const toggleLayer = (event, options={}) => {
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

const createLayerToggles = (layer, parent, map, layerGroup, geojson) => {
    const mapContainer = map.getContainer()
    
    const handler = (layer, parent) => {
        const formCheck = createFormCheck(`${mapContainer.id}_${layer._leaflet_id}`, {
            formCheckClass: 'fw-medium',
            label: layer.title,
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
    
        let bounds
        try {
            bounds = layer.getBounds()
        } catch {
            bounds = L.latLngBounds(layer.getLatLng(), layer.getLatLng())
        }

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
    
    const mainToggle = handler(layer, parent)
    const mainCheckbox = mainToggle.querySelector('input')
    if (layer._layers) {
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

        mainCheckbox.addEventListener('click', (event) => {
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
            const layerToggle = handler(feature, collapse)
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
        mainToggle.classList.add('pe-3')
        mainCheckbox.addEventListener('click', (event) => {
            toggleLayer(event, {
                map: map,
                layer: layer,
                layerGroup: layerGroup,
            })
        })    

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

const assignDefaultLayerStyle = (layer, options={}) => {
    let color = options.color
    if (!color) {
        color = 'hsl(0, 100%, 50%)'
    }

    let is_multipoint = layer.feature && layer.feature.geometry.type === 'MultiPoint'

    if (layer._latlng || is_multipoint) {
        const handler = (layer) => {
            let strokeColor = 'grey'
            if (color.startsWith('hsl')) {
                [h,s,l] = color.split(',').map(str => parseNumberFromString(str))
                l = l / 2
                strokeColor = `hsl(${h}, ${s}%, ${l}%)`
            }
    
            const div = document.createElement('div')
            div.className = 'h-100 w-100 rounded-circle'
            div.style.backgroundColor = color
            div.style.border = '1px solid strokeColor'
    
            var style = L.divIcon({
                className: 'bg-transparent',
                html: div.outerHTML,
            });
            
            layer.setIcon(style)
        }

        if (is_multipoint) {
            layer.eachLayer(i => handler(i))
        } else {
            handler(layer)
        }
    } else {
        const properties = {
            color: color,
            opacity: 1,
            fillOpacity: 0,
            weight:1,
        }

        if (options.fillColor) {
            let fillColor = 'white'
            if (color.startsWith('hsl')) {
                [h,s,l] = color.split(',').map(str => parseNumberFromString(str))
                l = (l / 2 * 3)
                fillColor = `hsl(${h}, ${s}%, ${l > 100 ? 100 : l}%)`
            }

            properties.fillColor = fillColor
            properties.fillOpacity = 0.25
        }

        const style = properties
        layer.setStyle(style)
    }
}