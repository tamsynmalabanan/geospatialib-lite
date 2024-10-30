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

    Array().concat(
        Array.from(map.getContainer().querySelectorAll('.leaflet-bar a')),
        Array.from(map.getContainer().querySelectorAll('.leaflet-bar button')),
    ).forEach(control => {
        control.classList.add(
            'btn', 
            'p-0',
            'text-reset',
            'text-decoration-none',
            'border-0',
            'rounded-0',
        )

        setAsThemedControl(control)
    })

    setAsThemedControl(map.attributionControl.getContainer())

    map.getContainer().querySelectorAll('.leaflet-control-scale-line')
    .forEach(scale => setAsThemedControl(scale))
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
        search: L.layerGroup(),
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
            accordion.id = `${mapId}_infoPanelAccordion`
            accordion.classList.add(
                'info-panel-accordion',
                'accordion',
                'accordion-flush',
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
                toggle.setAttribute('title', options.toggle_title)
                setAsThemedControl(toggle)
                toggle.classList.add('btn', 'btn-sm', 'position-relative')
                if (!options.collapsed) {
                    toggle.classList.add('callout-button')
                }
                toggle.classList.remove('accordion-button')
                labelElement(toggle, {
                    icon_class: options.icon_class,
                    label: name,
                    label_class: 'd-none d-lg-inline',
                })
                toggles.appendChild(toggle)

                toggle.addEventListener('click', () => {
                    if (toggle.classList.contains('collapsed')) {
                        toggle.classList.remove('callout-button')
                    } else {
                        toggle.parentElement
                        .querySelectorAll('.callout-button')
                        .forEach(toggle => toggle.classList.remove('callout-button'))
                        toggle.classList.add('callout-button')
                    }
                })
                
                const collapse = createAccordionCollapse(id, accordion.id, options.collapsed)
                accordion.appendChild(collapse)

                collapse.addEventListener('shown.bs.collapse', () => {
                    console.log(collapse)
                })

                const body = document.createElement('div')
                setAsThemedControl(body)
                body.classList.add('accordion-body', 'd-flex', 'rounded')
                collapse.appendChild(body)
            
                const resizeInfoPanel = () => {
                    const mapContainerHeight = mapContainer.clientHeight
                    const mapContainerWidth = mapContainer.clientWidth
                    body.style.maxHeight = `${mapContainerHeight * 0.8}px`;
                    if (mapContainerWidth > 1000) {
                        body.style.maxWidth = `${mapContainerWidth * 0.4}px`;
                    } else {
                        body.style.maxWidth = `${mapContainerWidth * 0.7}px`;
                    }
                }

                resizeInfoPanel()
                let resizeInfoPanelTimeout
                map.on('resize', () => {
                    clearTimeout(resizeInfoPanelTimeout)
                    resizeInfoPanelTimeout = setTimeout(resizeInfoPanel, 200)
                })

                return body
            }

            if (includedPanels.includes('legend')) {                
                const body = constructInfoPanel('Legend', {
                    toggle_title: 'Toggle legend panel',
                    icon_class: 'bi bi-stack',
                    collapsed: true,
                })
                body.innerText = 'legend content here'
            }
            
            if (includedPanels.includes('query')) {
                const body = constructInfoPanel('Query', {
                    toggle_title: 'Toggle query panel',
                    icon_class: 'bi bi-question-circle-fill',
                    collapsed: true
                })
                body.innerText = 'query content here'
            }
            
            return container
        }
    
        control.addTo(map)
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener("map:init", function (event) {
        const map = event.detail.map

        handleMapContainer(map)
        handleMapSize(map)
        handleMapControls(map)
        handleMapBasemap(map)
        handleMapLayerGroups(map)
        handleMapInfoPanels(map)

    })
})