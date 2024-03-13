function injectJSWithDomain() {
    var headElement = document.head || document.documentElement;
    var scriptElement = document.createElement('script');
    fetch(chrome.runtime.getURL('inject.js'))
        .then(response => response.text())
        .then(code => {
            headElement.insertBefore(scriptElement, headElement.firstElementChild);
            console.log("SCRIPT INSERTED!");
        })
        .catch(error => console.error('Error loading inject.js:', error));
}

// Listening to messages from the background script to inject inject.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'backgroundMessage') {
        console.log('Domain received!');
        injectJSWithDomain();
    }
});