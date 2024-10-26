const generateRandomPassword = (length) => {
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+";
    let password = "";
  
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charset.length);
        password += charset.charAt(randomIndex);
    }
  
    return password;
}

const resizeCaptcha = (reCAPTCHA) => {
  if (window.innerWidth > 400) {
    reCAPTCHA.style.transform = `scale(1)`
  } else {
    const captchaWidth = reCAPTCHA.children[0].offsetWidth
    const parentWidth = reCAPTCHA.parentElement.offsetWidth
    const scale = parentWidth / captchaWidth
  
    reCAPTCHA.style.transform = `scale(${scale})`
  }
}
  
const handleCAPTCHAFields = (parent) => {
    const captchaFields = parent.querySelectorAll('.g-recaptcha')
 
    if (captchaFields.length !== 0) {
        const currentTheme = getPreferredTheme()
        captchaFields.forEach(field => {
            field.setAttribute('data-theme', currentTheme)
            
            field.style.transformOrigin = 'center center'
            observeInnerHTML(field, () => {
                resizeCaptcha(field)

                const iframes = field.querySelectorAll('iframe[title="reCAPTCHA"]')
                if (iframes.length !== 0) {
                    iframes.forEach(frame => {
                        frame.setAttribute('class', 'rounded border')
                    })
                }
            })
            
            window.addEventListener('resize', () => {
                resizeCaptcha(field)
            })
        })
    } 
}

document.addEventListener('DOMContentLoaded', () => {
  handleCAPTCHAFields(document)
})

document.addEventListener('htmx:afterSwap', (event) => {
  handleCAPTCHAFields(event.target)
})

document.addEventListener('setTheme', () => {
    const iframes = document.querySelectorAll('.g-recaptcha iframe[title="reCAPTCHA"]')
    if (iframes.length !== 0) {
        const currentTheme = getPreferredTheme()
        iframes.forEach(frame => {
            let currentSource = frame.getAttribute('src')
            newSource = changeURLParamValue(currentSource, 'theme', currentTheme)
            frame.setAttribute('src', newSource)
        })
    }
})