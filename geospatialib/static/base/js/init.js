const handleActiveAccordionNavTabs = (link) => {
    link.setAttribute('disabled', true)
    link.style.fontWeight = 'bold'
    link.style.marginTop = '0px'
    link.style.border = "1px solid var(--bs-border-color)"
    link.style.borderBottom = "1px solid " + window.getComputedStyle(link).backgroundColor
}

const handleInactiveAccordionNavTabs = (link) => {
    link.removeAttribute('disabled')
    link.style.fontWeight = 'normal'
    link.style.marginTop = '-1px'
    link.style.border = "1px solid transparent"
}

const handleAccordionNavTabs = (parent, init=true) => {
    const accordionNavTabs = parent.querySelectorAll('.nav-tabs .accordion-button')
    accordionNavTabs.forEach(link => {

        if (!link.classList.contains('collapsed')) {
            handleActiveAccordionNavTabs(link)
        } else {
            handleInactiveAccordionNavTabs(link)
        }

        if (init) {
            link.addEventListener('click', (event) => {
                accordionNavTabs.forEach(otherLink => {
                    if (link === otherLink) {
                        handleActiveAccordionNavTabs(otherLink)
                    } else {
                        handleInactiveAccordionNavTabs(otherLink)
                    }
                })
            })
        }
    })
}

document.addEventListener('DOMContentLoaded', () => {
    handleAccordionNavTabs(document)
})

document.addEventListener('setTheme', () => {
    handleAccordionNavTabs(document, init=false)
})

document.addEventListener('hx_main:afterSwap', (event) => {
    handleAccordionNavTabs(event.target)
})