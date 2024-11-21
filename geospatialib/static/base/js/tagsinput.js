const handleTagsInputFields = (parent) => {
    const tagsInputFields = parent.querySelectorAll('input[data-role="tagsinput"]');
    tagsInputFields.forEach(field => {
        $(field).tagsinput()
        
        const container = field.parentElement
        
        const tagsinputContainer = container.querySelector('.bootstrap-tagsinput')
        tagsinputContainer.scrollTop = tagsinputContainer.scrollHeight
        tagsinputContainer.classList.add('gap-2', 'hide-scrollbar')
        setAsThemedControl(tagsinputContainer)
        
        Array.from(tagsinputContainer.children).forEach(child => {
            setAsThemedControl(child)

            if (child.tagName === 'INPUT') {
                child.id = `${field.id}_new`
                child.setAttribute('name', `${field.getAttribute('name')}_new`)
                child.classList.add('flex-grow-1')
            }
        })
        
        Array('itemAdded', 'itemRemoved').forEach(trigger => {
            $(field).on(trigger, (e) => {
                const event = new Event('tagsinput:change', { bubbles: true });
                field.dispatchEvent(event);
            });
        })

        const list = field.getAttribute('list')
        if (list) {
            const datalist = container.querySelector(`#${list}`)
            const input = tagsinputContainer.querySelector('input')
            input.setAttribute('list', list)
            input.addEventListener('input', (event) => {
                if (input.value.length !== 0) {
                    const event = new Event('input', { bubbles: true });
                    datalist.dispatchEvent(event);
                }
            });
        }

        if (event.type === 'htmx:afterSwap' && event.detail.requestConfig.triggeringEvent.type === 'tagsinput:change') {
            const targetId = event.detail.requestConfig.triggeringEvent.target.id
            if (field.id === targetId) {
                document.querySelector(`#${targetId}_new`).focus()
            }
        }
    })
}

document.addEventListener('htmx:afterSwap', (event) => {
    let parent = event.target
    if (parent.parentElement) {
        parent = parent.parentElement
    }

    handleTagsInputFields(parent)
})

document.addEventListener('DOMContentLoaded', () => {
    handleTagsInputFields(document)
})