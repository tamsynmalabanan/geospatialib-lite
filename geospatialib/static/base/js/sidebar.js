const toggleSidebar = (event) => {
    const id = 'geospatialibSidebar'
    const offcanvas = document.getElementById(id)
    const toggle = document.querySelector(`[data-bs-toggle="offcanvas"][data-bs-target="#${id}"]`)
    const toggleContainer = toggle.parentElement.parentElement
    const dismiss = document.querySelector(`[data-bs-dismiss="offcanvas"][data-bs-target="#${id}"]`)
    const footer = offcanvas.querySelector('.footer')

    if (offcanvas.classList.contains('offcanvas-lg')) {
        offcanvas.classList.remove('offcanvas-lg')
        offcanvas.classList.add('offcanvas')
    
        toggleContainer.classList.remove('d-lg-none')    
        
        dismiss.classList.remove('d-lg-none')

        footer.classList.remove('d-lg-flex')
    } else {
        offcanvas.classList.remove('offcanvas', 'show')
        offcanvas.classList.add('offcanvas-lg')
        offcanvas.removeAttribute('aria-modal', 'role')
        
        toggle.click()
        toggleContainer.classList.add('d-lg-none')
        
        dismiss.classList.add('d-lg-none')
        
        footer.classList.add('d-lg-flex')
    }
}