const toggleSidebar = (event) => {
    const id = 'geospatialibSidebar'
    const offcanvas = document.getElementById(id)
    
    if (offcanvas.classList.contains('offcanvas-lg')) {
        offcanvas.classList.remove('offcanvas-lg')
        offcanvas.classList.add('offcanvas')
    
        const toggle = document.querySelector(`[data-bs-toggle="offcanvas"][data-bs-target="#${id}"]`)
        const toggleContainer = toggle.parentElement
        toggleContainer.classList.remove('d-lg-none')
    
        const dismiss = document.querySelector(`[data-bs-dismiss="offcanvas"][data-bs-target="#${id}"]`)
        dismiss.classList.remove('d-lg-none')
    } else {
        offcanvas.classList.remove('offcanvas', 'show')
        offcanvas.classList.add('offcanvas-lg')
        offcanvas.removeAttribute('aria-modal', 'role')
    
        const toggle = document.querySelector(`[data-bs-toggle="offcanvas"][data-bs-target="#${id}"]`)
        toggle.click()
        const toggleContainer = toggle.parentElement
        toggleContainer.classList.add('d-lg-none')
    
        const dismiss = document.querySelector(`[data-bs-dismiss="offcanvas"][data-bs-target="#${id}"]`)
        dismiss.classList.add('d-lg-none')
    }
}