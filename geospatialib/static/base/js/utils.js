const getStoredTheme = () => localStorage.getItem('theme')
    
const setStoredTheme = theme => {
    localStorage.setItem('theme', theme)
}

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
      return storedTheme
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const setAsThemedControl = (element) => {
    const tagName = element.tagName.toLowerCase()
    if (tagName === 'button' || element.classList.contains('btn')) {
        element.classList.add(`btn-${getPreferredTheme()}`)
    } else {
        element.classList.add(`text-bg-${getPreferredTheme()}`)
    }
}

const getThemedControls = () => {
    return [
        {
            elements: document.querySelectorAll(`[onclick='toggleDarkMode(event)']`),
            classes: {
                light: ['bi-moon'],
                dark: ['bi-moon-fill'],
            }
        },
        {
            elements: Array().concat(
                Array.from(document.querySelectorAll(`.btn-light`)),
                Array.from(document.querySelectorAll(`.btn-dark`)),
            ),
            classes: {
                light: ['btn-light'],
                dark: ['btn-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(document.querySelectorAll(`.btn-outline-light`)),
                Array.from(document.querySelectorAll(`.btn-outline-dark`)),
            ),
            classes: {
                light: ['btn-outline-light'],
                dark: ['btn-outline-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(document.querySelectorAll(`.text-bg-light`)),
                Array.from(document.querySelectorAll(`.text-bg-dark`))
            ),
            classes: {
                light: ['text-bg-light'],
                dark: ['text-bg-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(document.querySelectorAll(`.leaflet-basemap-light`)),
                Array.from(document.querySelectorAll(`.leaflet-basemap-dark`))
            ),
            classes: {
                light: ['leaflet-basemap-light'],
                dark: ['leaflet-basemap-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(document.querySelectorAll(`.bg-light`)),
                Array.from(document.querySelectorAll(`.bg-dark`))
            ),
            classes: {
                light: ['bg-light'],
                dark: ['bg-dark'],
            }
        },
    ]
}

const toggleControlsTheme = (theme) => {
    getThemedControls().forEach(control => {
        control.elements.forEach(element => {
            for (let themeName in control.classes) {
                const themeClasses = control.classes[themeName]
                if (themeName === theme) {
                    themeClasses.forEach(className => {
                        element.classList.add(className)
                    })
                } else {
                    themeClasses.forEach(className => {
                        element.classList.remove(className)
                    })
                }
            }
        })
    })
}

const setTheme = theme => {
    if (theme === 'auto') {
        theme = getPreferredTheme()
    }
    
    document.documentElement.setAttribute('data-bs-theme', theme)
    setStoredTheme(theme)
    toggleControlsTheme(theme)
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