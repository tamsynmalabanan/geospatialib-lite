document.addEventListener("submit", (event) => {
    if (event.target.tagName === 'FORM' && event.target.classList.contains('htmx-form')) {
        event.preventDefault();
    }
});