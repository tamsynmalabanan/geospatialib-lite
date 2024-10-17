const getMapDataset = (map) => {
    return map.getContainer().parentElement.dataset
}

const handleMapContainer = (map) => {
    const container = map.getContainer()
    container.classList.add('z-1', `text-bg-${getPreferredTheme()}`)
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

    const controlsContainer = map._controlContainer
    const controls = Array.from(
        controlsContainer.querySelectorAll('.leaflet-bar a')
    ).concat(
        Array.from(controlsContainer.querySelectorAll('.leaflet-bar button'))
    )

    controls.forEach(control => {
        getControlClasses().forEach(className => {
            control.classList.add(className)
        })
    })

    const attribution = controlsContainer.querySelector('.leaflet-control-attribution')
    attribution.classList.add(`text-bg-${getPreferredTheme()}`)
}

const handleMapBasemap = (map) => {
    L.tileLayer("//tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        className: `leaflet-basemap leaflet-basemap-${getPreferredTheme()}`
    }).addTo(map);
}

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener("map:init", function (event) {
        const map = event.detail.map

        handleMapContainer(map)
        handleMapSize(map)
        handleMapControls(map)
        handleMapBasemap(map)

    })
})