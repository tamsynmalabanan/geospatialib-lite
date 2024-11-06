const getMapDataset = (map) => {
    return map.getContainer().parentElement.dataset
}

const handleMapContainer = (map) => {
    const container = map.getContainer()
    container.classList.add('z-1')
    setAsThemedControl(container)
    container.className = `${container.className} ${getMapDataset(map).leafletMapClass}`
}

const handleMapSize = (map) => {
    let mapResizeTimeout
    const container = map.getContainer()
    const resizeObserver = new ResizeObserver(entries => {
        for (const entry of entries) {
            if (entry.target.classList.contains('leaflet-container')) {
                clearTimeout(mapResizeTimeout);
                mapResizeTimeout = setTimeout(() => {
                    map.invalidateSize()
                }, 100)
            }
        }
    });
    resizeObserver.observe(container);
}

const handleMapControls = (map) => {
    const includedControls = getMapDataset(map).leafletControlsIncluded
    const excludedControls = getMapDataset(map).leafletControlsExcluded

    const mapControls = getMapControls()
    for (let controlName in mapControls) {
        const excluded = excludedControls && (excludedControls.includes(controlName) || excludedControls === 'all')
        const included = !includedControls || includedControls.includes(controlName) || includedControls === 'all'
        mapControls[controlName](map, included && !excluded)
    }

    const container = map.getContainer()
    Array().concat(
        Array.from(container.querySelectorAll('.leaflet-bar a')),
        Array.from(container.querySelectorAll('.leaflet-bar button')),
    ).forEach(control => {
        control.classList.add(
            'btn', 
            'p-0',
            'text-reset',
            'text-decoration-none',
            'border-0',
        )

        setAsThemedControl(control)
    })

    setAsThemedControl(map.attributionControl.getContainer())

    map.getContainer().querySelectorAll('.leaflet-control-scale-line')
    .forEach(scale => setAsThemedControl(scale))

    const leafletControls = container.querySelectorAll('.leaflet-control')
    leafletControls.forEach(control => {
        Array('mouseover', 'touchstart').forEach(trigger => {
            control.addEventListener(trigger, (e) => {
                map.dragging.disable()
                map.touchZoom.disable()
                map.doubleClickZoom.disable()
                map.scrollWheelZoom.disable()
            })
        })    

        Array('mouseout', 'touchend').forEach(trigger => {
            control.addEventListener(trigger, (e) => {
                map.dragging.enable()
                map.touchZoom.enable()
                map.doubleClickZoom.enable()
                map.scrollWheelZoom.enable()
            })
        })
    })
}

const handleMapBasemap = (map) => {
    L.tileLayer("//tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        className: `leaflet-basemap leaflet-basemap-${getPreferredTheme()}`
    }).addTo(map);
}

const handleMapLayerGroups = (map) => {
    const layerGroups = {
        client: L.layerGroup(),
        library: L.layerGroup(),
        query: L.layerGroup(),
    }

    for (let group in layerGroups) {
        const layerGroup = layerGroups[group]
        layerGroup.show = () => map.addLayer(layerGroup)
        layerGroup.hide = () => map.removeLayer(layerGroup)
        layerGroup.show()
    }

    map.getLayerGroups = () => layerGroups
}

const constructInfoPanel = (map, name, options={}) => {
    const mapContainer = map.getContainer()
    const mapId = mapContainer.id

    const id = `${mapId}_infoPanel${name.replace(' ', '')}`
    const toggle = createAccordionToggle(id)
    toggle.setAttribute('title', options.toggleTitle)
    mapContainer.querySelector('.info-panel-toggles').appendChild(toggle)

    setAsThemedControl(toggle)
    toggle.classList.remove('accordion-button')
    toggle.classList.add('btn', 'btn-sm', 'position-relative')
    if (!options.collapsed) {
        toggle.classList.add('pointer-bottom')
    }

    labelElement(toggle, {
        iconClass: options.iconClass,
        label: name,
        labelClass: 'd-none d-lg-inline',
    })

    toggle.addEventListener('click', () => {
        if (toggle.classList.contains('collapsed')) {
            toggle.classList.remove('pointer-bottom')
        } else {
            toggle.parentElement
            .querySelectorAll('.pointer-bottom')
            .forEach(toggle => toggle.classList.remove('pointer-bottom'))
            toggle.classList.add('pointer-bottom')
        }
    })
    
    const accordion = mapContainer.querySelector('.info-panel-accordion')
    const collapse = createAccordionCollapse(id, accordion.id, options.collapsed)
    accordion.appendChild(collapse)
    
    const header = document.createElement('h6')
    header.classList.add('p-3', 'm-0', 'fw-semibold', 'fs-14', 'd-flex', 'gap-5', 'justify-content-between')
    collapse.appendChild(header)

    const span = document.createElement('span')
    span.innerText = name
    header.appendChild(span)

    const collapseToggle = document.createElement('button')
    collapseToggle.className = 'border-0 bg-transparent px-0 text-muted bi bi-chevron-up'
    header.appendChild(collapseToggle)
    
    collapseToggle.addEventListener('click', () => hideAllSubCollapse(collapse))
    
    const body = document.createElement('div')
    body.classList.add('accordion-body', 'd-flex', 'flex-column', 'overflow-auto', 'px-3', 'py-0')
    collapse.appendChild(body)

    const resizeInfoPanel = () => {
        const mapContainerHeight = mapContainer.clientHeight
        const mapContainerWidth = mapContainer.clientWidth

        const topMargin = Math.floor(body.getBoundingClientRect().top) - Math.floor(mapContainer.getBoundingClientRect().top)

        let siblingsHeight = 0
        Array.from(collapse.children).forEach(element => {
            if (element != body) {
                const height = parseInt(window.getComputedStyle(element).height)
                if (height) {
                    siblingsHeight += height
                }
            }
        })

        body.style.maxHeight = `${(mapContainerHeight * 0.9)-topMargin-siblingsHeight}px`;
        
        if (mapContainerWidth > 1000) {
            body.style.maxWidth = `${mapContainerWidth * 0.3}px`;
        } else {
            body.style.maxWidth = `${mapContainerWidth * 0.8}px`;
        }
    }

    let resizeInfoPanelTimeout
    const resizeInfoPanelOnTimeout = () => {
        clearTimeout(resizeInfoPanelTimeout)
        resizeInfoPanelTimeout = setTimeout(resizeInfoPanel, 200)
    }

    map.on('resize', resizeInfoPanelOnTimeout)
    toggle.addEventListener('click', resizeInfoPanel)

    return body
}

const handleMapLegend = (map) => {
    const mapContainer = map.getContainer()
    const mapId = mapContainer.id

    const body = constructInfoPanel(map, 'Legend', {
        toggleTitle: 'Toggle legend panel',
        iconClass: 'bi bi-stack',
        collapsed: true,
    })

    map.on('layeradd', (event) => {
        const layer = event.layer
        if (layer.data && layer.data.layerStyles) {
            const styles = JSON.parse(layer.data.layerStyles)
            if (Object.keys(styles).length !== 0) {
                const url = styles[Object.keys(styles)[0]].legend
                if (url) {
                    const legendContainer = createButtonAndCollapse(
                        `${mapId}Legend_${layer._leaflet_id}`, {
                            label: layer.data.layerLabel
                        }
                    )
                    legendContainer.classList.add('mb-3')
                    body.insertBefore(legendContainer, body.firstChild)

                    const legendCollapse = legendContainer.querySelector('.collapse')
                    legendCollapse.appendChild(createImgElement(url, 'Legend not found.'))

                    const legendToggle = legendContainer.querySelector('button')
                    legendToggle.classList.add('bg-transparent', 'border-0', 'px-0', 'fs-6', 'text-start')
                }
            } 
        }
    })

    map.on('layerremove', (event) => {
        const id = `${mapId}Legend_${event.layer._leaflet_id}`
        const legendToggle = body.querySelector(`#${id}`)
        if (legendToggle) {
            legendToggle.parentElement.remove()
        }
    })
}

const handleMapQuery = (map) => {
    const mapContainer = map.getContainer()
    const mapId = mapContainer.id

    const body = constructInfoPanel(map, 'Query', {
        toggleTitle: 'Toggle query panel',
        iconClass: 'bi bi-question-circle-fill',
        collapsed: false
    })

    const header = body.parentElement.querySelector('h6')
    header.querySelector('button').remove()
    const queryButton = createButton({
        buttonClass: 'border fs-14 bi bi-question-circle-fill ms-auto d-flex flex-nowrap',
        labelClass: 'text-nowrap',
        parent: header,
    })

    const footer = document.createElement('div')
    footer.className = 'border-top p-3 d-flex flex-wrap'
    body.parentElement.appendChild(footer)

    const disableMapQuery = () => {
        map._queryEnabled = false
        mapContainer.style.cursor = ''
    }

    const toggleQueryButton = () => {
        if (getMeterScale(map) <= 100000) {
            if (!map._querying) {
                queryButton.removeAttribute('disabled')
                const span = document.createElement('span')
                span.className = 'font-monospace fs-12 text-wrap'
                span.innerText = 'Query enabled.'
                footer.innerHTML = span.outerHTML
            }
        } else {
            disableMapQuery()
            queryButton.setAttribute('disabled', true)
            if (!map._querying) {
                const span = document.createElement('span')
                span.className = 'font-monospace fs-12 text-wrap'
                span.innerText = 'Zoom in to at least 100 km scale to enable query.'
                footer.innerHTML = span.outerHTML
            }
        }
    }

    mapContainer.addEventListener('mapInitComplete', toggleQueryButton)
    map.on('zoomend', toggleQueryButton)
    map.on('resize', toggleQueryButton)

    map._queryEnabled = false
    queryButton.addEventListener('click', (e) => {
        L.DomEvent.stopPropagation(e);
        L.DomEvent.preventDefault(e);
        
        if (map._queryEnabled === false) {
            map._queryEnabled = true
            mapContainer.style.cursor = 'pointer'
        } else {
            disableMapQuery()
        }
    })

    const fetchQueryData = async (event) => {
        map._querying = true
        disableMapQuery()
        queryButton.setAttribute('disabled', true)
        footer.innerText = 'Running query...'
        
        map.getLayerGroups().query.clearLayers()
        body.innerHTML = ''    

        const queryResults = document.createElement('ul')
        queryResults.className = 'list-group list-group-flush fs-14'
        queryResults.id = 'queryResults'

        const toolbar = createFormCheck('queryResultsToggleAll', {
            formCheckClass: 'fs-14 mb-3 sticky-top',
            checkboxAttrs: {
                'data-layers-toggles': '#queryResults',
                'data-layers-label': 'feature',
                'disabled': 'true',
                'onclick': 'toggleOffAllLayers(this)',
            },
            labelClass: 'text-muted',
            button: true,
            buttonClass: 'bi bi-chevron-expand text-muted',
            buttonCallback: () => hideAllSubCollapse(queryResults),
            parent: body
        })
        setAsThemedControl(toolbar)
        body.appendChild(queryResults)
        
        const coordsGeoJSON = L.marker(event.latlng).toGeoJSON()
        const coordsLayer = L.geoJSON(coordsGeoJSON).getLayers()[0]
        coordsLayer.title = `Query location: ${Number(event.latlng.lat.toFixed(6))} ${Number(event.latlng.lng.toFixed(6))}`
        assignDefaultLayerStyle(coordsLayer, {color:'hsl(111, 100%, 54%)'})
        const [coordsToggle, coordsCollapse] = createLayerToggles(coordsLayer, queryResults, map, 'query')
        coordsToggle.classList.add('mb-3')
        coordsToggle.querySelector('input').click()

        const fetchers = {}
    
        const libraryLayers = map.getLayerGroups().library.getLayers()
        if (libraryLayers.length > 0) {
            libraryLayers.forEach(layer => {
                fetchers[layer.data.layerLabel] = fetchData(event, layer)
            })
        }

        fetchers['OpenStreetMap'] = fetchOSMData(event, {maximum:100})

        const data = await Promise.all(Object.values(fetchers)) 

        for (let i = 0; i <= data.length-1; i++) {
            const geojson = data[i]
            if (geojson) {
                handleGeoJSON(geojson, coordsGeoJSON.geometry)
                const geoJSONLayer = L.geoJSON(geojson)
                geoJSONLayer.title = Object.keys(fetchers)[i]
                geoJSONLayer.eachLayer(layer => {
                    layer.title = getLayerTitle(layer)
                    layer.bindTooltip(layer.title, {sticky:true})
                    assignDefaultLayerStyle(layer, {
                        color:'hsl(111, 100%, 54%)',
                        fillColor:true,
                    })
                })
                createLayerToggles(geoJSONLayer, queryResults, map, 'query', geojson)

                const attribution = document.createElement('div')
                attribution.innerHTML = `<pre class='m-0 mb-3 fs-12 text-wrap ps-1'>${geojson.licence}</pre>`
                queryResults.appendChild(attribution)

            }
        }

        map._querying = false
        toggleQueryButton()
        footer.innerText = 'Query complete.'        
    }

    map._querying = false
    map.on('click', (event) => {
        if (map._queryEnabled) {
            fetchQueryData(event)
        }
    })
}

const handleMapInfoPanels = (map) => {
    const includedPanels = getMapDataset(map).leafletInfoPanels
    if (includedPanels) {
        const mapContainer = map.getContainer()
        const mapId = mapContainer.id

        const control = L.control({position:'topright'})
        control.onAdd = (map) => {
            const container = L.DomUtil.create('div', 'info-panel')
            container.classList.add(
                'd-flex',
                'flex-column',
                'justify-content-end',
                'gap-2',
            )
        
            const accordion = document.createElement('div')
            setAsThemedControl(accordion)
            accordion.id = `${mapId}_infoPanelAccordion`
            accordion.classList.add(
                'info-panel-accordion',
                'accordion',
                'accordion-flush',
                'rounded',
            )
            
            const toggles = document.createElement('div')
            toggles.id = `${mapId}_infoPanelToggles`
            toggles.classList.add(
                'info-panel-toggles',
                'd-flex',
                'justify-content-end',
                'gap-2',
            )

            container.appendChild(toggles)
            container.appendChild(accordion)
                
            return container
        }
    
        const infoPanelControl = control.addTo(map)
        const infoPanelContainer = infoPanelControl.getContainer()

        if (includedPanels.includes('legend')) {
            handleMapLegend(map)
        }
        
        if (includedPanels.includes('query')) {
            handleMapQuery(map)
        }

        map.fire('resize')
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener("map:init", function (event) {
        const map = event.detail.map

        handleMapBasemap(map)
        handleMapLayerGroups(map)
        handleMapContainer(map)
        handleMapSize(map)
        handleMapInfoPanels(map)
        handleMapControls(map) // needs to be after handleMapInfoPanels

        const newEvent = new Event('mapInitComplete')
        map.getContainer().dispatchEvent(newEvent)
    })
})