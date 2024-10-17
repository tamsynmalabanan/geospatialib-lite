const getMapControls = () => {
    return {
        zoom: zoomBar,
        scale: scaleBar,
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
