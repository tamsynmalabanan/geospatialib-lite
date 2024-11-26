let shareDatasetBounds
let shareDatasetLayerLoadErrorTimeout

const getShareDatasetSubmitBtn = () => document.querySelector('#shareDatasetModal .btn[type="submit"]')
const getShareDatasetNameField = () => document.querySelector('#shareDatasetModal [name="name"]')
const getShareDatasetMap = () => mapQuerySelector('#shareDatasetModal .leaflet-container')

const disableShareDatasetSubmitBtn = () => {
    getShareDatasetSubmitBtn().setAttribute('disabled', true)
}

const resetShareDatasetSubmitBtn = () => {
    clearTimeout(shareDatasetLayerLoadErrorTimeout)
    disableShareDatasetSubmitBtn()
}

const handleShareDatasetForm = (bounds) => {
    if (bounds) {
        bounds = bounds.replace('(', '[').replace(')', ']')
        shareDatasetBounds = JSON.parse(bounds)
    } else {
        shareDatasetBounds = undefined
    }
    disableShareDatasetSubmitBtn()
    clearAllLayers(getShareDatasetMap())
}

const shareDatasetLayerLoaded = (event) => {
    clearTimeout(shareDatasetLayerLoadErrorTimeout)

    const submitButton = getShareDatasetSubmitBtn()
    if (!shareDatasetBounds) {
        submitButton.removeAttribute('disabled')
    }

    const nameField = getShareDatasetNameField()
    if (nameField.classList.contains('is-invalid')) {
        nameField.classList.remove('is-invalid')
        
        const invalidFeedback = nameField.parentElement.querySelector('.invalid-feedback')
        invalidFeedback.textContent = ''
    }
}

const shareDatasetLayerLoadError = (event) => {
    disableShareDatasetSubmitBtn()

    const nameField = getShareDatasetNameField()
    if (!nameField.classList.contains('is-invalid')) {
        nameField.classList.add('is-invalid')
        
        const invalidFeedback = nameField.parentElement.querySelector('.invalid-feedback')
        invalidFeedback.textContent = 'Layer is not loading within the current map extent. Provided the the URL and format are valid, it may load when you zoom in or span to other parts of the map.'
    }    
}

const renderSharedDatasetLayer = () => {
    const map = getShareDatasetMap()
    if (map) {
        const formElements = document.querySelector('#shareDatasetModal form').elements
        const fields = {
            layerUrl: formElements.url, 
            layerFormat: formElements.format,
            layerName: formElements.name,
        }

        if (Object.values(fields).every(field => !field.classList.contains('is-invalid') && field.value !== '')) {
            const data = {}
            for (const key in fields) {
                data[key] = fields[key].value
            }
            
            const layer = createLayerFromURL(data)
            if (layer) {
                assignLayerLoadEventHandlers(
                    layer, 
                    shareDatasetLayerLoaded,
                    shareDatasetLayerLoadError,
                )
        
                map.getLayerGroups().client.addLayer(layer)
            }
        
            if (shareDatasetBounds) {
                const [minX, minY, maxX, maxY] = shareDatasetBounds
                const bounds = L.latLngBounds([[minY, minX], [maxY, maxX]]);
                map.fitBounds(bounds)
            }
        }

    }
}