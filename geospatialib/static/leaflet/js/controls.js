const getMapControls = () => {
    return {
        zoom: zoomBar
    }
}

const getControlClasses = () => Array(
    'btn', 
    `btn-${getPreferredTheme()}`, 
    'p-0',
    'text-reset',
    'text-decoration-none',
    'border-0',
    'rounded-0',
)

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