let sharedDatasetExists

const getShareDatasetSubmitBtn = () => document.querySelector('#shareDatasetModal .btn[type="submit"]')
const getShareDatasetNameField = () => document.querySelector('#shareDatasetModal [name="name"]')
const getShareDatasetMap = () => mapQuerySelector('#shareDatasetModal .leaflet-container')

const disabledShareDatasetSubmitBtn = () => {
    getShareDatasetSubmitBtn().setAttribute('disabled', true)
}

const handleShareDatasetForm = (dataset) => {
    disabledShareDatasetSubmitBtn()
    clearAllLayers(getShareDatasetMap())
}

const shareDatasetLayerLoaded = (event) => {
    const submitButton = getShareDatasetSubmitBtn()
    if (!sharedDatasetExists) {
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
    disabledShareDatasetSubmitBtn()

    const nameField = getShareDatasetNameField()
    if (!nameField.classList.contains('is-invalid')) {
        nameField.classList.add('is-invalid')
        
        const invalidFeedback = nameField.parentElement.querySelector('.invalid-feedback')
        invalidFeedback.textContent = 'Layer is not loading within the current map extent. Try to zoom in or span to other parts of the map.'
    }    
}

const renderSharedDatasetLayer = () => {
    const form = document.querySelector('#shareDatasetModal form')
    const data = {
        layerPath: form.elements.path.value, 
        layerFormat: form.elements.format.value,
        layerName: form.elements.name.value,
    }

    const layer = createLayerFromURL(data)
    if (layer) {
        assignLayerLoadEventHandlers(
            layer, 
            shareDatasetLayerLoaded,
            shareDatasetLayerLoadError,
        )

        const map = getShareDatasetMap()
        if (map) {
            map.getLayerGroups().client.addLayer(layer)
        }
    }
}