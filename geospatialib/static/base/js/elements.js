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

    if (options.iconClass) {
        const icon = document.createElement('i')
        icon.className = options.iconClass
        element.appendChild(icon)
    }

    if (options.label) {
        const span = document.createElement('span')

        if (options.labelClass) {
            span.className = options.labelClass
        }

        if (options.iconClass) {
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

const createFormCheck = (id, options={}) => {
    const formCheck = document.createElement('div')
    formCheck.className = `form-check d-flex flex-grow-1 ${options.formCheckClass}`

    const checkbox = document.createElement('input')
    checkbox.id = id
    checkbox.className = `form-check-input ${options.checkboxClass}`
    checkbox.setAttribute('type', 'checkbox')
    if (options.checkboxAttrs) {
        for (const key in options.checkboxAttrs) {
            checkbox.setAttribute(key, options.checkboxAttrs[key])
        }
    }
    formCheck.appendChild(checkbox)

    const label = document.createElement('label')
    label.className = `${options.labelClass}`
    label.setAttribute('for', id)
    formCheck.appendChild(label)

    if (options.label) {
        const span = document.createElement('span')
        span.innerText = options.label
        label.appendChild(span)
    }

    if (options.button) {
        const button = document.createElement('button')
        button.setAttribute('type', 'button')
        button.setAttribute('title', options.buttonTitle)
        button.className = `bg-transparent border-0 p-0 ms-auto ${options.buttonClass}`
        formCheck.appendChild(button)
        if (options.buttonCallback) {
            button.addEventListener('click', options.buttonCallback)
        }
    }

    return formCheck
}