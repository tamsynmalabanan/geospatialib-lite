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
    element.classList.add('d-flex', 'flex-nowrap')

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