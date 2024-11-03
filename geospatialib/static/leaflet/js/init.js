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
            toggles.classList.add(
                'info-panel-toggles',
                'd-flex',
                'justify-content-end',
                'gap-2',
            )

            container.appendChild(toggles)
            container.appendChild(accordion)
    
            const constructInfoPanel = (name, options={}) => {
                const id = `${mapId}_infoPanel${name.replace(' ', '')}`
                const toggle = createAccordionToggle(id)
                toggle.setAttribute('title', options.toggleTitle)
                setAsThemedControl(toggle)
                toggle.classList.add('btn', 'btn-sm', 'position-relative')
                if (!options.collapsed) {
                    toggle.classList.add('pointer-bottom')
                }
                toggle.classList.remove('accordion-button')
                labelElement(toggle, {
                    iconClass: options.iconClass,
                    label: name,
                    labelClass: 'd-none d-lg-inline',
                })
                toggles.appendChild(toggle)

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
                
                collapseToggle.addEventListener('click', () => {
                    const collapseElements = collapse.querySelectorAll('.collapse')
                    collapseElements.forEach(element => {
                        if (element.classList.contains('show')) {
                            const bsCollapse = new bootstrap.Collapse(element)
                            bsCollapse.hide()
                        }
                    })
                })
                
                const body = document.createElement('div')
                body.classList.add('accordion-body', 'd-flex', 'flex-column', 'overflow-auto', 'px-3', 'py-0')
                collapse.appendChild(body)
            
                const resizeInfoPanel = () => {
                    const mapContainerHeight = mapContainer.clientHeight
                    const mapContainerWidth = mapContainer.clientWidth
                    
                    const headerHeight = parseInt(window.getComputedStyle(header).height)
                    const togglesHeight = parseInt(window.getComputedStyle(toggles).height)
                    
                    body.style.maxHeight = `${(mapContainerHeight * 0.9)-20-headerHeight-togglesHeight}px`;
                    
                    if (mapContainerWidth > 1000) {
                        body.style.maxWidth = `${mapContainerWidth * 0.4}px`;
                    } else {
                        body.style.maxWidth = `${mapContainerWidth * 0.7}px`;
                    }
                }

                let resizeInfoPanelTimeout
                map.on('resize', () => {
                    clearTimeout(resizeInfoPanelTimeout)
                    resizeInfoPanelTimeout = setTimeout(resizeInfoPanel, 200)
                })

                toggle.addEventListener('click', () => map.fire('resize'))

                return body
            }

            if (includedPanels.includes('legend')) {
                const body = constructInfoPanel('Legend', {
                    toggleTitle: 'Toggle legend panel',
                    iconClass: 'bi bi-stack',
                    collapsed: true,
                })

                map.on('layeradd', (event) => {
                    const layer = event.layer
                    if (layer.data && layer.data.layerStyles) {
                        const styles = JSON.parse(layer.data.layerStyles)
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
                })

                map.on('layerremove', (event) => {
                    const id = `${mapId}Legend_${event.layer._leaflet_id}`
                    const legendToggle = body.querySelector(`#${id}`)
                    if (legendToggle) {
                        legendToggle.parentElement.remove()
                    }
                })
            }
            
            if (includedPanels.includes('query')) {
                const body = constructInfoPanel('Query', {
                    toggleTitle: 'Toggle query panel',
                    iconClass: 'bi bi-question-circle-fill',
                    collapsed: false
                })

                const queryButton = createButton({
                    buttonClass: 'border fs-14 bi bi-question-circle-fill mb-3 ms-auto d-flex flex-nowrap',
                    labelClass: 'text-nowrap',
                    parent: body,
                })

                const resultContainer = document.createElement('div')
                body.appendChild(resultContainer)

                const footer = document.createElement('div')
                footer.className = 'border-top mb-3 px-2 pt-3 mt-4 font-monospace fs-12'
                body.appendChild(footer)
                
                const disableMapQuery = () => {
                    map._queryEnabled = false
                    mapContainer.style.cursor = ''
                }

                const toggleQueryButton = () => {
                    if (getScale(map, 'km') <= 100) {
                        queryButton.removeAttribute('disabled')
                        if (getScale(map, 'km') <= 10) {
                            footer.innerText = 'Query enabled.'
                        } else {
                            footer.innerText = 'Query enabled. Zoom in to at least 10 km to query OSM.'
                        }
                    } else {
                        disableMapQuery()
                        queryButton.setAttribute('disabled', true)
                        footer.innerText = 'Zoom in to at least 100 km scale to enable query.'
                    }
                }

                mapContainer.addEventListener('mapInitComplete', toggleQueryButton)
                map.on('zoomend', toggleQueryButton)

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

                const fetchQueryDataError = (msg) => {
                    const errorMessage = document.createElement('span')
                    errorMessage.className = 'px-2 font-monospace fs-12'
                    errorMessage.innerText = msg
                    resultContainer.innerHTML = errorMessage.outerHTML
                }

                const fetchQueryData = async (event) => {
                    if (map._queryEnabled) {
                        disableMapQuery()

                        const fetchers = {}
                        
                        const libraryLayers = map.getLayerGroups().library.getLayers()
                        if (libraryLayers.length > 0) {
                            libraryLayers.forEach(layer => {
                                console.log(layer.data)
                            })
                        }
    
                        if (getScale(map, 'km') <= 10) {
                            fetchers['OpenStreetMap'] = fetchOSMData(map)
                        }
    
                        if (Object.keys(fetchers).length > 0) {
                            queryButton.setAttribute('disabled', true)
                            footer.innerText = 'Running query...'
                            resultContainer.innerHTML = ''
                            
                            const data = await Promise.all(Object.values(fetchers)) 
                            
                            if (data.every(i => !i)) {
                                fetchQueryDataError('Query did not return any feature.')
                            } else {
                                const fetchedData = {}
                                for (let i = 0; i <= data.length-1; i++) {
                                    fetchedData[Object.keys(fetchers)[i]] = data[i]
                                }
    
                                console.log(fetchedData)
                            }
    
                            queryButton.removeAttribute('disabled')
                            footer.innerText = 'Query complete.'
                        } else {
                            fetchQueryDataError("No queryable layers on the map.")
                        }
                    }
                }

                map.on('click', fetchQueryData)

                // const toolbar = createFormCheck('queryResultsToggleAll', {
                //     formCheckClass: 'fs-14',
                //     checkboxAttrs: {
                //         'data-layers-toggles': '#queryResults',
                //         'data-layers-shown': '0',
                //         'disabled': 'true',
                //         'onclick': 'toggleOffAllLayers(this)',
                //     },
                //     labelClass: 'text-muted',
                //     button: true,
                //     buttonClass: 'bi bi-chevron-expand'
                // })

                // body.appendChild(toolbar)
            }
            
            return container
        }
    
        control.addTo(map)
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