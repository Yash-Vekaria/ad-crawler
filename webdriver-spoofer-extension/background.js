window.tabId = -1;

// Inject JS inside an iframe at OnBeforeNavigated stage of its loading
function injectInsideIframes(iframe) {
    window.tabId = iframe.tabId;
    window.frameId = iframe.frameId;
    
    chrome.tabs.get(window.tabId, function(tab) {
        setTimeout(() => {
            chrome.tabs.executeScript(
                window.tabId, { 
                    frameId: window.frameId, 
                    file: "content.js", 
                    matchAboutBlank: true 
                },
                function(result) {
                    console.log(`Tab ID: ${window.tabId} | Frame ID: ${window.frameId}`);
                    chrome.tabs.sendMessage(window.tabId, {
                        type: 'backgroundMessage'
                    });
                }
            );
        }, 5);
    });
}

// Injecting content.js inside each iframe
chrome.webNavigation.onBeforeNavigate.addListener(injectInsideIframes);

// Listen for clicks on the extension icon to display the message
chrome.browserAction.onClicked.addListener(function(tab) {
    console.log(`Extension icon clicked on Tab: ${tab.id}`);
});