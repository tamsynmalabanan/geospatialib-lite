const getMapControls = () => {
    return {
        zoom: zoomBar,
        scale: scaleBar,
        search: searchBar,
        reset: resetView,
        locate: locateUser,
    }
}

const zoomBar = (map, include=true) => {    
    if (include) {
        const buttons = {
            _zoomInButton: ['bi', 'bi-plus', 'rounded-top', 'pt-1', 'rounded-bottom-0'],
            _zoomOutButton: ['bi', 'bi-dash', 'rounded-bottom', 'rounded-top-0'],
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
            // collapsed: true,
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

        const alternativesList = geocoderContainer.querySelector('.leaflet-control-geocoder-alternatives')
        alternativesList.classList.add('list-unstyled', 'px-2')

        const geocoderFieldsSelector = map.getContainer().parentElement.getAttribute('data-leaflet-geocoder-fields')
        if (geocoderFieldsSelector) {
            document.addEventListener('change', (event) => {
                if (event.target.matches(geocoderFieldsSelector)) {
                    const place = event.target.value
                    if (place !== '') {
                        geocoder.setQuery(place)
                        geocoder._geocode()
                    }
                }
            })
            
            geocoder.on('markgeocode', (e) => {
                const geocoderFields = document.querySelectorAll(geocoderFieldsSelector)
                geocoderFields.forEach(field => {
                    if (field.value.toLowerCase() === e.target._lastGeocode.toLowerCase()) {
                        field.value = e.geocode.name
                    }
                })
            })
        }
    }
}

const resetView = (map, include) => {
    const resetViewControl = map.resetviewControl
    if (include) {
        const container = resetViewControl.getContainer()
        const control = container.querySelector('a')
        control.classList.add('rounded', 'bi', 'bi-globe-americas', 'fs-6')
        
        const defautMapBounds = map.getBounds()
        resetViewControl.getBounds = () => defautMapBounds

        control.addEventListener('click', () => {
            map._viewReset = true
        })
    } else {
        map.removeControl(resetViewControl)
    }
}

const locateUser = (map, include) => {
    
}