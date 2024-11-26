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
        layerGroup.show = () => {
            if (group === 'query') {
                const queryPane = map.createPane('queryPane')
                queryPane.style.zIndex = 625
                map.addLayer(layerGroup, {
                    pane:'queryPane'
                })
            } else {
                map.addLayer(layerGroup)
            }

        }
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
    body.classList.add('accordion-body', 'd-flex', 'flex-column', 'overflow-auto', 'p-0')
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
            body.parentElement.style.maxWidth = `${mapContainerWidth * 0.3}px`;
        } else {
            body.parentElement.style.maxWidth = `${mapContainerWidth * 0.8}px`;
        }
    }

    let resizeInfoPanelTimeout
    const resizeInfoPanelOnTimeout = () => {
        clearTimeout(resizeInfoPanelTimeout)
        resizeInfoPanelTimeout = setTimeout(resizeInfoPanel, 200)
    }

    map.on('resize', resizeInfoPanelOnTimeout)
    toggle.addEventListener('click', resizeInfoPanel)
    observeInnerHTML(body, resizeInfoPanel)

    return body
}

const handleMapLegend = (map) => {
    const mapContainer = map.getContainer()
    const mapId = mapContainer.id

    const body = constructInfoPanel(map, 'Legend', {
        toggleTitle: 'Toggle legend panel',
        iconClass: 'bi bi-stack',
        collapsed: false,
    })

    map.on('layeradd', (event) => {
        const layer = event.layer
        if (layer.data) {
            const containerId = `${mapId}Legend_${layer._leaflet_id}`

            const legendContainer = createButtonAndCollapse(
                containerId, {
                    label: layer.data.layerLabel,
                    buttonClassName: 'text-wrap'
                }
            )
            legendContainer.classList.add('mb-3', 'px-3')
            body.insertBefore(legendContainer, body.firstChild)

            const legendCollapse = legendContainer.querySelector('.collapse')
            
            if (layer.data.layerLegendUrl) {
                legendCollapse.appendChild(createImgElement(layer.data.layerLegendUrl, 'Legend not found.'))
            }
            
            if (layer.data.layerLegendObj) {
                layer.on('legend_updated', () => {
                    legendCollapse.innerHTML = ''
                    
                    const styles = JSON.parse(layer.data.layerLegendObj)
                    Object.keys(styles).forEach(name => {
                        const style = styles[name]

                        const container = document.createElement('div')
                        container.className = 'd-flex gap-2'
                        legendCollapse.appendChild(container)

                        const icon = document.createElement('div')
                        icon.className = 'align-self-center'
                        icon.style.height = '10px'
                        container.appendChild(icon)

                        let labelText = name
                        if (style.count > 1) {
                            labelText = labelText + ` (${style.count})`
                        }

                        const label = document.createElement('div')
                        label.innerText = labelText
                        container.appendChild(label)

                        const styleDef = style.style
                        if (style.type === 'Point') {
                            icon.style.width = '10px'
                            icon.innerHTML = styleDef.options.html
                        } else {
                            icon.style.width = '15px'
                            
                            let color = styleDef.color
                            if (!color) {
                                color = 'hsla(0, 100%, 50%, 1)'
                            }

                            const [h,s,l,a] = color.split(',').map(str => parseNumberFromString(str))
                            
                            let opacity = styleDef.opacity
                            if (!opacity) {
                                opacity = 1
                            }
                            
                            let weight = styleDef.weight
                            if (!weight) {
                                weight = 1
                            }
                            
                            const box = document.createElement('div')
                            icon.appendChild(box)
                            box.style.border = `${weight}px solid hsla(${h}, ${s}%, ${l}%, ${opacity})`

                            if (style.type === 'LineString') {
                                icon.style.height = '0px'
                                box.className = 'h-0 w-100'
                            }
                            
                            if (style.type === 'Polygon') {
                                box.className = 'h-100 w-100'

                                const fillColor = styleDef.fillColor
                                const fillOpacity = styleDef.fillOpacity
                                
                                if (fillColor && fillOpacity) {
                                    const [fillh,fills,filll,filla] = fillColor.split(',').map(str => parseNumberFromString(str))
                                    box.style.backgroundColor = `hsla(${fillh}, ${fills}%, ${filll}%, ${fillOpacity})`
                                }
                            }
                        }

                    })

                    
                })
            }

            const legendToggle = legendContainer.querySelector('button')
            legendToggle.classList.add('bg-transparent', 'border-0', 'px-0', 'fs-6', 'text-start')
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

    const body = constructInfoPanel(map, 'Query', {
        toggleTitle: 'Toggle query panel',
        iconClass: 'bi bi-question-circle-fill',
        collapsed: true,
    })

    const header = body.parentElement.querySelector('h6')
    header.querySelector('button').remove()

    const footer = document.createElement('div')
    footer.className = 'border-top p-3 d-flex flex-wrap font-monospace'
    body.parentElement.appendChild(footer)

    
    
    const queryDropdown = document.createElement('div')
    queryDropdown.className = 'dropdown ms-auto'
    header.appendChild(queryDropdown)

    const queryToggle = createButton({
        buttonClass: 'dropdown-toggle px-2 py-0',
        buttonAttrs: {
            'type': 'button',
            'data-bs-toggle': 'dropdown',
            'aria-expanded': 'false'
        },
        labelClass: 'text-nowrap',
        parent: queryDropdown,
    })

    queryToggle.appendChild(createSpanElement({className:'bi bi-question-circle-fill me-1'}))

    const queryMenu = document.createElement('div')
    queryMenu.className = 'dropdown-menu fs-14'
    queryDropdown.appendChild(queryMenu)

    const layersQueryBtn = createDropdownMenuListItem({
        label: 'Query layers', 
        parent: queryMenu,
        buttonAttrs: {
            'data-query-osm': 'false'
        }
    }).querySelector('button')

    const layersOSMQueryBtn = createDropdownMenuListItem({
        label: 'Query layers & OSM', 
        parent: queryMenu,
        buttonAttrs: {
            'data-query-osm': 'true'
        }
    }).querySelector('button')

    const queryOSMBtn = createDropdownMenuListItem({
        label: 'Query OSM in map view', 
        parent: queryMenu,
        buttonAttrs: {
            'disabled': true
        }
    }).querySelector('button')
    
    const divider = document.createElement('li')
    divider.className = 'dropdown-divider'
    queryMenu.appendChild(divider)

    const cancelQueryBtn = createDropdownMenuListItem({
        label: 'Cancel query', 
        parent: queryMenu,
        buttonAttrs: {
            'disabled': true
        }
    }).querySelector('button')

    const clearQueryBtn = createDropdownMenuListItem({
        label: 'Clear query features', 
        parent: queryMenu,
        buttonAttrs: {
            'disabled': true
        }
    }).querySelector('button')



    const clearQueryResults = () => {
        map.getLayerGroups().query.clearLayers()
        body.innerHTML = ''
        clearQueryBtn.setAttribute('disabled', true)
    }

    const disableMapQuery = () => {
        map._queryEnabled = false
        enableLayerClick(map)
        mapContainer.style.cursor = ''
        if (!map._querying) {
            cancelQueryBtn.setAttribute('disabled', true)
        }
    }

    const disableQueryBtns = () => {
        if (queryMenu.classList.contains('show')) {
            queryToggle.click()
        }

        Array(queryOSMBtn, layersQueryBtn, layersOSMQueryBtn).forEach(btn => {
            btn.setAttribute('disabled', true)
        })

        if (!map._querying) {
            cancelQueryBtn.setAttribute('disabled', true)
        }
    }

    const toggleQueryButtons = () => {
        const scale = getMeterScale(map)
        if (scale <= 100000) {
            if (!map._querying) {
                Array(layersQueryBtn, layersOSMQueryBtn).forEach(btn => {
                    btn.removeAttribute('disabled')
                })
                const span = document.createElement('span')
                span.className = 'font-monospace fs-12 text-wrap'
                span.innerText = 'Query enabled.'
                footer.innerHTML = span.outerHTML
            }
        } else {
            disableMapQuery()
            disableQueryBtns()

            if (!map._querying) {
                const span = document.createElement('span')
                span.className = 'font-monospace fs-12 text-wrap'
                span.innerText = 'Zoom in to at least 100-km scale to enable query.'
                footer.innerHTML = span.outerHTML
            }
        }
        
        if (scale <= 10000) {
            queryOSMBtn.removeAttribute('disabled')
        } else {
            queryOSMBtn.setAttribute('disabled', true)
        }

    }

    map.on('zoomend resize mapInitComplete', toggleQueryButtons)

    map._queryEnabled = false
    Array(layersQueryBtn, layersOSMQueryBtn).forEach(btn => {
        btn.addEventListener('click', (e) => {
            L.DomEvent.stopPropagation(e);
            L.DomEvent.preventDefault(e);
            
            map._queryEnabled = true
            disableLayerClick(map)
            mapContainer.style.cursor = 'pointer'
            map._queryOSM = btn.getAttribute('data-query-osm') === "true"

            cancelQueryBtn.removeAttribute('disabled')
        })
    })

    queryOSMBtn.addEventListener('click', (event) => {
        if (getMeterScale(map) <= 10000) {
            fetchQueryData(L.rectangle(map.getBounds()).toGeoJSON(), {'OpenStreetMap':{
                label: 'OpenStreetMap',
                data: fetchOSMDataInBbox(getMapBbox(map), {abortBtn:cancelQueryBtn})
            }}).then(queryResults => {
                if (queryResults && queryResults.children.length === 1) {
                    createSpanElement({
                        label: 'There are too many features within the query area. Zoom in to a smaller extent and try again.',
                        className: 'mb-3 fs-12 font-monospace',
                        parent: queryResults
                    })    
                }
            })
        } else {
            const span = document.createElement('span')
            span.className = 'font-monospace fs-12 text-wrap'
            span.innerText = 'Zoom in to at least 10-km scale to query OSM in map view.'
            footer.innerHTML = span.outerHTML
        }
    })

    cancelQueryBtn.addEventListener('click', () => {
        map._queryCancelled = true
        disableMapQuery()
    })

    clearQueryBtn.addEventListener('click', () => {
        clearQueryResults()
    })

    const collectFetchers = (event) => {
        const fetchers = {}
    
        const libraryLayers = map.getLayerGroups().library.getLayers()
        if (libraryLayers.length > 0) {
            libraryLayers.forEach(layer => {
                const data = layer.data
                fetchers[`${data.layerUrl}:${data.layerFormat}:${data.layerName}`] = {
                    label: data.layerLabel,
                    data: fetchLibraryData(event, layer, {abortBtn:cancelQueryBtn}),
                }
            })
        }

        if (map._queryOSM) {
            fetchers['OpenStreetMap'] = {
                label: 'OpenStreetMap',
                data: fetchOSMData(event, {abortBtn:cancelQueryBtn}),
            }
        }

        return fetchers
    }

    const fetchQueryData = async (defaultGeoJSON, fetchers) => {
        map._queryCancelled = false
        map._querying = true

        disableMapQuery()
        disableQueryBtns()
        clearQueryResults()

        cancelQueryBtn.removeAttribute('disabled')

        footer.innerText = 'Running query...'
        
        const queryResults = document.createElement('ul')
        queryResults.className = 'list-group list-group-flush fs-14 w-100 overflow-auto px-3'
        queryResults.id = 'queryResults'

        const toolbar = createFormCheck('queryResultsToggleAll', {
            formCheckClass: 'fs-14 ms-3 mb-3 pe-3',
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
        
        const color = 'hsla(111, 100%, 50%, 1)'
        const defaultLayer = L.geoJSON(defaultGeoJSON).getLayers()[0]
        defaultLayer.options.pane = 'queryPane'
        defaultLayer.title = `Query location`
        assignDefaultLayerStyle(defaultLayer, {color:color})
        const [coordsToggle, coordsCollapse] = createLayerToggles(defaultLayer, queryResults, map, 'query')
        coordsToggle.classList.add('mb-3')
        coordsToggle.querySelector('input').click()

        if (Object.keys(fetchers).length > 0) {
            const handler = async (geojson, title) => {
                defaultGeom = defaultGeoJSON.geometry
                await handleGeoJSON(geojson, {
                    defaultGeom:defaultGeom,
                    sort:true,
                    featureId:true,
                })
                
                const geoJSONLayer = L.geoJSON(geojson, {
                    pointToLayer: (geoJsonPoint, latlng) => {
                        return L.marker(latlng, {icon:getDefaultLayerStyle('point', {color:color})})
                    },
                    style: (geoJsonFeature) => {
                        return getDefaultLayerStyle('other', {color:color, fillColor:true, weight:2})
                    },        
                    onEachFeature: (feature, layer) => {
                        layer.options.pane = 'queryPane'
                        layer.title = getLayerTitle(layer)
                        layer.bindTooltip(layer.title, {sticky:true})

                        if (Object.keys(feature.properties).length > 0) {
                            const createPopup = () => {
                                layer.bindPopup(createFeaturePropertiesTable(feature.properties).outerHTML, {
                                    autoPan: false,
                                }).openPopup()
                                layer.off('click', createPopup)
                            }

                            layer.on('click', createPopup)
                        }
                    }    
                })

                geoJSONLayer.title = title
                createLayerToggles(geoJSONLayer, queryResults, map, 'query', geojson)

                const layerFooter = document.createElement('div')
                layerFooter.className = 'mb-3 '
                queryResults.appendChild(layerFooter)

                layerFooter.innerHTML = `<pre class='m-0 fs-12 text-wrap ps-1 font-monospace'>${geojson.licence}</pre>`
                if (geojson.note) {
                    const span = document.createElement('p')
                    span.className = 'm-0 fs-10 text-wrap ps-1 pt-1 font-monospace text-muted text-justify lh-1'
                    span.innerText = geojson.note
                    layerFooter.appendChild(span)
                }
            }

            const data = await Promise.all(Object.values(fetchers).map(value => value.data)) 
            for (let i = 0; i <= data.length-1; i++) {
                if (data[i] && data[i].features && data[i].features.length > 0) {
                    const label = Object.values(fetchers).map(value => value.label)[i]
                    await handler(data[i], label)
                }
            }
        } else {
            createSpanElement({
                label: 'No queryable layers shown on map.',
                className: 'mb-3 fs-12 font-monospace',
                parent: queryResults
            })
        }

        map._querying = false
        toggleQueryButtons()
        cancelQueryBtn.setAttribute('disabled', true)
        if (map._queryCancelled) {
            clearQueryResults()
            footer.innerText = 'Query cancelled.'
            return
        } else {
            clearQueryBtn.removeAttribute('disabled')
            footer.innerText = 'Query complete.'
            return queryResults
        }
    }

    map._querying = false
    map.on('click', (event) => {
        if (map._queryEnabled) {
            defaultGeoJSON = L.marker(event.latlng).toGeoJSON()
            fetchQueryData(defaultGeoJSON, collectFetchers(event))
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
    
        control.addTo(map)

        if (includedPanels.includes('legend')) {
            handleMapLegend(map)
        }
        
        if (includedPanels.includes('query')) {
            handleMapQuery(map)
        }

        map.fire('resize')
    }
}

const handleMapObservers = (map) => {
    map.on('popupopen', (event) => {
        const wrapper = event.popup._container.querySelector('.leaflet-popup-content-wrapper')
        wrapper.classList.add(`text-bg-${getPreferredTheme()}`, 'overflow-auto')
        wrapper.style.maxHeight = `${map.getSize().y * 0.5}px`
        event.popup._container.querySelector('.leaflet-popup-tip').classList.add(`bg-${getPreferredTheme()}`)
    })

    const bboxFieldsSelector = getMapDataset(map).leafletBboxFields
    if (bboxFieldsSelector) {
        const updateBboxFields = () => {
            const bboxFields = document.querySelectorAll(bboxFieldsSelector)
            bboxFields.forEach(field => {
                const bounds = loopThroughCoordinates(map.getBounds(), validateCoordinates)
                const geom = JSON.stringify(L.rectangle(bounds).toGeoJSON().geometry)
                field.value = geom
            })
        }        

        updateBboxFields(map)
        
        let updateBboxFieldsTimeout
        map.on('resize moveend zoomend updateBboxFields', (event) => {
            clearTimeout(updateBboxFieldsTimeout)
            updateBboxFieldsTimeout = setTimeout(() => {
                updateBboxFields(map)
            }, 100)
        })
    }
}

// const handleMapTitle = (map) => {
//     const title = getMapDataset(map)['leafletMapTitle']
//     if (title) {
//         const control = L.control({position:'topleft'})
//         control.onAdd = (map) => {
//             const container = L.DomUtil.create('div', 'leaflet-map-title')
//             setAsThemedControl(container)
//             container.classList.add(
//                 'rounded',
//                 'px-3',
//                 'py-2',
//                 'bg-opacity-75',
//             )
            
//             const header = document.createElement('h4')
//             container.appendChild(header)
//             header.className = 'm-0'
//             header.innerText = title
            
//             return container
//         }

//         const container = control.addTo(map).getContainer()

//         const topLeftContainer = map._controlCorners.topleft
//         if (topLeftContainer.firstChild !== container) {
//             topLeftContainer.insertBefore(container, topLeftContainer.firstChild);
//         }
//     }
// }

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener("map:init", function (event) {
        const map = event.detail.map

        handleMapBasemap(map)
        handleMapLayerGroups(map)
        handleMapContainer(map)
        handleMapSize(map)
        handleMapInfoPanels(map)
        handleMapControls(map) // needs to be after handleMapInfoPanels
        handleMapObservers(map)

        map.initComplete = true
        map.fire('mapInitComplete')
    })
})