const handleActiveAccordionNavTabs = (link) => {
    link.setAttribute('disabled', true)
    link.style.fontWeight = 'bold'
    link.style.marginTop = '0px'
    link.style.boxShadow = 'none'
    link.style.border = "1px solid var(--bs-border-color)"
    link.style.borderBottom = "1px solid " + window.getComputedStyle(link).backgroundColor
    link.classList.remove('border-0')
}

const handleInactiveAccordionNavTabs = (link) => {
    link.classList.add('border-0')
    link.removeAttribute('disabled')
    link.style.fontWeight = 'normal'
    link.style.marginTop = '-1px'
    link.style.border = "1px solid transparent"
}

const handleAccordionNavTabs = (parent, init=true) => {
    const handler = (link) => {
        if (!link.classList.contains('collapsed')) {
            handleActiveAccordionNavTabs(link)
        } else {
            handleInactiveAccordionNavTabs(link)
        }    
    }

    parent.querySelectorAll('.nav-tabs .accordion-button').forEach(link => {
        if (init) {
            link.classList.remove('bg-transparent')

            link.addEventListener('click', (event) => {
                document.querySelectorAll('.nav-tabs .accordion-button').forEach(otherLink => handler(otherLink))
            })
        }

        handler(link)
    })
}

document.addEventListener('DOMContentLoaded', () => {
    handleAccordionNavTabs(document)
})

document.addEventListener('setTheme', () => {
    handleAccordionNavTabs(document, false)
})

document.addEventListener('htmx:afterSwap', (event) => {
    handleAccordionNavTabs(event.target)
})