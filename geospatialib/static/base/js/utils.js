const observeInnerHTML = (element, callback) => {
    let originalInnerHTML = element.innerHTML;
  
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' || mutation.type === 'characterData') {
                const newInnerHTML = element.innerHTML;
                if (newInnerHTML !== originalInnerHTML) {
                    callback(newInnerHTML);
                    originalInnerHTML = newInnerHTML;
                }
            }
        });
    });
  
    observer.observe(element, { childList: true, characterData: true });
  
    return observer;
}

const removeURLParams = () => {
    return window.history.pushState({}, '', window.location.href.split('?')[0]);
}

const changeURLParamValue = (url, param, value) => {
    const urlParts = new URL(url);
    urlParts.searchParams.set(param, value);
    return urlParts.toString();
}

const pushParamsToURL = (params) => {
    const urlParams = new URLSearchParams(window.location.search);
  
    for (const key in params) {
      urlParams.set(key, params[key]);
    }
  
    const newURL = `${window.location.origin}${window.location.pathname}?${urlParams.toString()}`;
    window.history.pushState({}, '', newURL);
}

const getURLParams = () => {
    const urlParams = new URLSearchParams(window.location.search)
    return Object.fromEntries(urlParams)
}

const generateShortUUID = () => {
    const uuid = crypto.randomUUID();
    const shortenedUUID = uuid.substring(0, 8);
    return shortenedUUID;
}