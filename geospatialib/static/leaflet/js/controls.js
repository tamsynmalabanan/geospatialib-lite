const getMapControls = () => {
    return {
        zoom: zoomBar,
        scale: scaleBar,
        search: searchBar,
    }
}

const zoomBar = (map, include=true) => {    
    if (include) {
        const buttons = {
            _zoomInButton: ['bi', 'bi-plus', 'rounded-top', 'pt-1'],
            _zoomOutButton: ['bi', 'bi-dash', 'rounded-bottom'],
        }

        for (let buttonName in buttons) {
            const button = map.zoomControl[buttonName]
            button.innerHTML = ''
            buttons[buttonName].forEach(className => {
                button.classList.add(className)
            });
        }
    } else {
        map.removeControl(map.zoomControl)
    }
}

const scaleBar = (map, include=true) => {
    if (include) {
        L.control.scale({ position: 'bottomright' }).addTo(map)
    }
}

const searchBar = (map, include=true) => {
    if (include) {
        const geocoder = L.Control.geocoder({
            defaultMarkGeocode: false,
            collapsed: true,
            position: 'topleft',
        })
        .on('markgeocode', (e) => {
            var bbox = e.geocode.bbox;
            var poly = L.polygon([
                bbox.getSouthEast(),
                bbox.getNorthEast(),
                bbox.getNorthWest(),
                bbox.getSouthWest()
            ]);
            map.fitBounds(poly.getBounds());
        })
        .addTo(map);

        const geocoderContainer = geocoder.getContainer()
        setAsThemedControl(geocoderContainer)

        const topLeftContainer = map._controlCorners.topleft
        if (topLeftContainer.firstChild !== geocoderContainer) {
            topLeftContainer.insertBefore(geocoderContainer, topLeftContainer.firstChild);
        }

        const button = geocoderContainer.querySelector('button')
        button.innerText = ''
        button.classList.add('bi','bi-binoculars-fill')
    }
}