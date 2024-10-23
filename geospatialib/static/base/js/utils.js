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

const changeURLParamValue = (url, param, value) => {
    const urlParts = new URL(url);
    urlParts.searchParams.set(param, value);
    return urlParts.toString();
}