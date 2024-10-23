const generateRandomPassword = (length) => {
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+";
    let password = "";
  
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * charset.length);
      password += charset.charAt(randomIndex);
    }
  
    return password;
}

const getCAPTCHASize = () => {
    if (window.innerWidth < 400) {
      return ['compact', 174, 152, 164, 155]
    } else {
      return ['normal', 302, 75, 302, 76]
    }
}

const handleCAPTCHAFields = (parent) => {
    const captchaFields = parent.querySelectorAll('.g-recaptcha')
  
    if (captchaFields.length !== 0) {
        let size = 'normal'
        if (window.innerWidth < 400) {
            size = 'compact'
        }
      
        const currentTheme = getPreferredTheme()
        captchaFields.forEach(field => {
            field.setAttribute('data-theme', currentTheme)
            field.setAttribute('data-size', size)

            observeInnerHTML(field, () => {
                const iframes = field.querySelectorAll('iframe[title="reCAPTCHA"]')
                if (iframes.length !== 0) {
                    const size = getCAPTCHASize()
                    iframes.forEach(frame => {
                        frame.setAttribute('class', 'rounded')

                        frame.setAttribute('width', size[1])
                        frame.setAttribute('height', size[2])
                        frame.parentElement.parentElement.style.width = `${size[3]}px`
                        frame.parentElement.parentElement.style.height = `${size[4]}px`
                    })
                }
            })
        })
    } 
}

document.addEventListener('DOMContentLoaded', () => {
  handleCAPTCHAFields(document)
})

document.addEventListener('htmx:afterSwap', (event) => {
  const target = event.target
  handleCAPTCHAFields(target)
})

document.addEventListener('setTheme', () => {
  const iframes = document.querySelectorAll('iframe[title="reCAPTCHA"]')
  if (iframes.length !== 0) {
      const currentTheme = getPreferredTheme()
      iframes.forEach(frame => {
          let currentSource = frame.getAttribute('src')
          newSource = changeURLParamValue(currentSource, 'theme', currentTheme)
          frame.setAttribute('src', newSource)
      })
  }
})

window.addEventListener('resize', () => {
  const iframes = document.querySelectorAll('iframe[title="reCAPTCHA"]')
  if (iframes.length !== 0) {
      const size = getCAPTCHASize()
      iframes.forEach(frame => {
          let currentSource = frame.getAttribute('src')
          newSource = changeURLParamValue(currentSource, 'size', size[0])
          frame.setAttribute('src', newSource)

          frame.setAttribute('width', size[1])
          frame.setAttribute('height', size[2])
          frame.parentElement.parentElement.style.width = `${size[3]}px`
          frame.parentElement.parentElement.style.height = `${size[4]}px`
      })
  }
});