const handleMapContainer = (map) => {
    const container = map.getContainer()
    container.classList.add('z-1')
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

document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener("map:init", function (event) {
        const map = event.detail.map

        handleMapContainer(map)
        handleMapSize(map)
    })
})