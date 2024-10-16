const getStoredTheme = () => localStorage.getItem('theme')
    
const setStoredTheme = theme => localStorage.setItem('theme', theme)

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
      return storedTheme
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const setTheme = theme => {
    if (theme === 'auto') {
        theme = (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    }
    
    document.documentElement.setAttribute('data-bs-theme', theme)
    setStoredTheme(theme)

    const toggles = document.querySelectorAll(`[onclick='toggleDarkMode(event)']`)
    if (theme === 'light') {
        toggles.forEach(toggle => {
            toggle.classList.remove('bi-moon-fill')
            toggle.classList.add('bi-moon')
        })
    } else {
        toggles.forEach(toggle => {
            toggle.classList.remove('bi-moon')
            toggle.classList.add('bi-moon-fill')
        })
    }

}

const toggleDarkMode = (event) => {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme')
    if (currentTheme === 'light') {
        setTheme('dark')
    } else {
        setTheme('light')
    }
}

document.addEventListener('DOMContentLoaded', () => {
    setTheme(getPreferredTheme())
})