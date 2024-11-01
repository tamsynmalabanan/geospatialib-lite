const createDropdownMenuListItem = (label) => {
    const li = document.createElement('li')

    const button = document.createElement('button')
    button.className = 'dropdown-item'
    button.innerText = label

    li.appendChild(button)

    return li
}

const createAccordionCollapse = (id, parentId, collapsed=true) => {
    const collapse = document.createElement('div')
    collapse.id = id
    collapse.classList.add('accordion-collapse', 'collapse')
    if (!collapsed) {
        collapse.classList.add('show')
    }
    collapse.setAttribute('data-bs-parent', `#${parentId}`)
    return collapse
}

const createAccordionToggle = (target, collapsed=true) => {
    const toggle = document.createElement('button')
    toggle.classList.add('accordion-button')
    toggle.setAttribute('type', 'button')
    toggle.setAttribute('data-bs-toggle', 'collapse')
    toggle.setAttribute('data-bs-target', `#${target}`)
    toggle.setAttribute('aria-controls', target)
    if (collapsed) {
        toggle.classList.add('collapsed')
        toggle.setAttribute('aria-expanded', 'false')
    } else {
        toggle.setAttribute('aria-expanded', 'true')
    }

    return toggle
}

const labelElement = (element, options={}) => {
    element.classList.add('d-flex', 'flex-nowrap', 'fw-medium')

    if (options.icon_class) {
        const icon = document.createElement('i')
        icon.className = options.icon_class
        element.appendChild(icon)
    }

    if (options.label) {
        const span = document.createElement('span')

        if (options.label_class) {
            span.className = options.label_class
        }

        if (options.icon_class) {
            span.classList.add('ms-2')
        }

        span.innerText = options.label
        element.appendChild(span)
    }

    
}

const createImgElement = (url, alt) => {
    const img = document.createElement('img')
    img.setAttribute('src', url)
    img.setAttribute('alt', alt)
    return img
}

const createButtonAndCollapse = (id, options={}) => {
    const container = document.createElement('div')
    container.classList.add('d-flex', 'flex-column', 'gap-2')

    const button = document.createElement('button')
    button.classList.add('fw-medium', 'dropdown-toggle')
    button.setAttribute('type', 'button')
    button.setAttribute('data-bs-toggle', 'collapse')
    button.setAttribute('data-bs-target', `#${id}`)
    button.setAttribute('aria-controls', id)
    if (options.collapsed) {
        button.classList.add('collapsed')
        button.setAttribute('aria-expanded', 'false')
    } else {
        button.setAttribute('aria-expanded', 'true')
    }
    if (options.label) {
        const span = document.createElement('span')
        span.classList.add('me-2', 'fs-14')
        span.innerText = options.label
        button.appendChild(span)
    }
    setAsThemedControl(button)
    container.appendChild(button)

    const collapse = document.createElement('div')
    collapse.id = id
    collapse.classList.add('collapse')
    if (!options.collapsed) {
        collapse.classList.add('show')
    }
    container.appendChild(collapse)

    return container
}