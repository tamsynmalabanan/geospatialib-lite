const toggleDarkMode = (event) => {
    const toggles = document.querySelectorAll(`[onclick='toggleDarkMode(event)']`)
    const currentTheme = document.documentElement.getAttribute('data-bs-theme')
    if (currentTheme === 'light') {
        document.documentElement.setAttribute('data-bs-theme', 'dark')
        toggles.forEach(toggle => {
            toggle.classList.remove('bi-moon-fill')
            toggle.classList.add('bi-moon')
        })
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'light')
        toggles.forEach(toggle => {
            toggle.classList.remove('bi-moon')
            toggle.classList.add('bi-moon-fill')
        })
    }
}