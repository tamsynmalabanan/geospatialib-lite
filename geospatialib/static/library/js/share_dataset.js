let sharedDataset
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

const handleShareDatasetForm = (dataset) => {
    sharedDataset = dataset
    disableShareDatasetSubmitBtn()
    clearAllLayers(getShareDatasetMap())
}

const shareDatasetLayerLoaded = (event) => {
    clearTimeout(shareDatasetLayerLoadErrorTimeout)

    const submitButton = getShareDatasetSubmitBtn()
    if (!sharedDataset) {
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
        const form = document.querySelector('#shareDatasetModal form')
        const data = {
            layerUrl: form.elements.url.value, 
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
    
            map.getLayerGroups().client.addLayer(layer)
            // shareDatasetLayerLoadErrorTimeout = setTimeout(shareDatasetLayerLoadError, 60000)
        }
    
        
        if (sharedDataset) {
            const bboxLayer = L.geoJSON(sharedDataset)
            map.fitBounds(bboxLayer.getBounds())
        }
    }
}