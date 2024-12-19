const deleteFormset = (formsetSelector, prefix) => {
    const formset = document.querySelector(formsetSelector)
    if (formset) {
        const deleteCheckbox = formset.querySelector(`[name="${prefix}-DELETE"]`)
        deleteCheckbox.value = 'on'
        formset.classList.add('d-none')
        dispatchChangeEventToFormsetFieldTarget(deleteCheckbox)
    }
}

const dispatchChangeEventToFormsetFieldTarget = (field) => {
    const target = document.querySelector(field.dataset.formsetField)
    const event = new Event('formset:change', { bubbles: true });
    target.dispatchEvent(event);
}

const handleFormsetFields = (parent) => {
    const formsetFields = parent.querySelectorAll('.formset-field')
    formsetFields.forEach(element => {
        element.addEventListener('change', () => {
            dispatchChangeEventToFormsetFieldTarget(element)
        })
    });
}

document.addEventListener('htmx:afterSwap', (event) => {
    let parent = event.target
    if (parent.parentElement) {
        parent = parent.parentElement
    }

    handleFormsetFields(parent)
})

document.addEventListener('DOMContentLoaded', () => {
    handleFormsetFields(document)
})