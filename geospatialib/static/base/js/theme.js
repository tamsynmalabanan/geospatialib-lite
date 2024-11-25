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

const getThemedControls = (parent=document) => {
    return [
        {
            elements: parent.querySelectorAll(`[onclick='toggleDarkMode(event)']`),
            classes: {
                light: ['bi-moon'],
                dark: ['bi-moon-fill'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.btn-light`)),
                Array.from(parent.querySelectorAll(`.btn-dark`)),
            ),
            classes: {
                light: ['btn-light'],
                dark: ['btn-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.btn-outline-light`)),
                Array.from(parent.querySelectorAll(`.btn-outline-dark`)),
            ),
            classes: {
                light: ['btn-outline-light'],
                dark: ['btn-outline-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.text-bg-light`)),
                Array.from(parent.querySelectorAll(`.text-bg-dark`))
            ),
            classes: {
                light: ['text-bg-light'],
                dark: ['text-bg-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.leaflet-basemap-light`)),
                Array.from(parent.querySelectorAll(`.leaflet-basemap-dark`))
            ),
            classes: {
                light: ['leaflet-basemap-light'],
                dark: ['leaflet-basemap-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.bg-light`)),
                Array.from(parent.querySelectorAll(`.bg-dark`))
            ),
            classes: {
                light: ['bg-light'],
                dark: ['bg-dark'],
            }
        },
        {
            elements: Array().concat(
                Array.from(parent.querySelectorAll(`.table-light`)),
                Array.from(parent.querySelectorAll(`.table-dark`))
            ),
            classes: {
                light: ['table-light'],
                dark: ['table-dark'],
            }
        },
    ]
}

const toggleControlsTheme = async (theme, parent=document) => {
    document.documentElement.setAttribute('data-bs-theme', theme)

    let toggleControlsThemeTimeout
    getThemedControls(parent).forEach(control => {
        control.elements.forEach(element => {
            for (let themeName in control.classes) {
                const themeClasses = control.classes[themeName];
                if (themeName === theme) {
                    themeClasses.forEach(className => {
                        element.classList.add(className);
                    });
                } else {
                    themeClasses.forEach(className => {
                        element.classList.remove(className);
                    });
                }
            }

            clearTimeout(toggleControlsThemeTimeout);
            toggleControlsThemeTimeout = setTimeout(() => {
                const setThemeEvent = new Event('setTheme');
                document.dispatchEvent(setThemeEvent);
            }, 250)
        });
    
    });}

const setTheme = theme => {
    if (theme === 'auto') {
        theme = getPreferredTheme()
    }
    
    setStoredTheme(theme)

    toggleControlsTheme(theme)
    // const setThemeEvent = new Event('setTheme')
    // document.dispatchEvent(setThemeEvent)
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

document.addEventListener('htmx:afterSwap', (event) => {
    let target = event.target
    
    if (target.parentElement) {
        target = target.parentElement
    }
    
    toggleControlsTheme(getPreferredTheme(), parent=target)
})