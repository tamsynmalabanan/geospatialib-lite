const getSidebarOffcanvas = () => {
    return document.getElementById('geospatialibSidebar')
}

const toggleSidebar = (event) => {
    const offcanvas = getSidebarOffcanvas()
    const toggle = document.querySelector(`[data-bs-toggle="offcanvas"][data-bs-target="#${offcanvas.id}"]`)
    const toggleContainer = toggle.parentElement.parentElement
    const dismiss = document.querySelector(`[data-bs-dismiss="offcanvas"][data-bs-target="#${offcanvas.id}"]`)
    const footer = offcanvas.querySelector('.footer')
    const gutter = offcanvas.querySelector('.gutter')

    if (offcanvas.classList.contains('offcanvas-lg')) {
        offcanvas.classList.remove('offcanvas-lg')
        offcanvas.classList.add('offcanvas')
    
        toggleContainer.classList.remove('d-lg-none')    
        
        dismiss.classList.remove('d-lg-none')

        footer.classList.remove('d-lg-flex')

        gutter.classList.remove('d-lg-flex')


    } else {
        offcanvas.classList.remove('offcanvas', 'show')
        offcanvas.classList.add('offcanvas-lg')
        offcanvas.removeAttribute('aria-modal', 'role')
        
        toggle.click()
        toggleContainer.classList.add('d-lg-none')
        
        dismiss.classList.add('d-lg-none')
        
        footer.classList.add('d-lg-flex')

        gutter.classList.add('d-lg-flex')
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const offcanvas = getSidebarOffcanvas()
    const sidebarGutter = offcanvas.querySelector('.gutter')
    Array('mousedown', 'touchstart').forEach(startTrigger => {
        sidebarGutter.addEventListener(startTrigger, (event) => {
            const offcanvasWidth = offcanvas.offsetWidth
            
            let startX = event.clientX
            if (event.type === 'touchstart') {
                startX = event.touches[0].clientX
            }
            
            const onMouseMoveResizeSidebar = (event) => {
                let moveX = event.clientX - startX
                if (event.type === 'touchmove') {
                    moveX = event.touches[0].clientX - startX
                }

                offcanvas.style.width =`${offcanvasWidth + moveX}px`;
            }
            
            Array('mousemove', 'touchmove').forEach(moveTrigger => {
                document.addEventListener(moveTrigger, onMouseMoveResizeSidebar)
            })
            
            const onMouseUpResizeSidebar = () => {
                const rowWidth = offcanvas.parentElement.offsetWidth
                const offcanvasWidth = offcanvas.offsetWidth

                let col = Math.floor(offcanvasWidth/(rowWidth/12))

                if (col > 0) {
                    if (col < 4) {
                        col = 4
                    }
    
                    if (col > 9) {
                        col = 9
                    }
    
                    offcanvas.classList.forEach(className => {
                        if (className.includes('col-lg-')) {
                            offcanvas.classList.remove(className)
                        }
                    })
    
                    offcanvas.classList.add(`col-lg-${col}`)
                } else {
                    toggleSidebar()
                }

                
                offcanvas.style.width = ''
                document.removeEventListener('mousemove', onMouseMoveResizeSidebar);
                document.removeEventListener('mouseup', onMouseUpResizeSidebar)
            }

            Array('mouseup', 'touchend').forEach(endTrigger => {
                document.addEventListener(endTrigger, onMouseUpResizeSidebar)
            })
        });
    })
})