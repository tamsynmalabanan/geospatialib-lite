const removeModalStaticBackdrop = (modalId) => {
    const modal = document.getElementById(modalId)
    if (modal && modal.getAttribute('data-bs-backdrop') === 'static') {
        modal.removeAttribute('data-bs-backdrop')
        modal.removeAttribute('data-bs-keyboard')
        const existingModal = bootstrap.Modal.getInstance(modal)
        if (existingModal) {
            existingModal.dispose();
            const newModal = new bootstrap.Modal(modal);
            newModal.show()
        }
    }

}