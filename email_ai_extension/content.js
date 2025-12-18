chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "get_content") {
    // Try multiple selectors because Gmail classes change frequently
    const bodySelectors = [
      ".a3s.aiL",      // Standard email body
      ".ii.gt",        // Alternative container
      "[role='main']"  // Fallback
    ];

    let emailText = "";
    for (const selector of bodySelectors) {
      const element = document.querySelector(selector);
      if (element && element.innerText.trim().length > 0) {
        emailText = element.innerText;
        break; 
      }
    }

    if (emailText) {
      sendResponse({ text: emailText });
    } else {
      sendResponse({ text: null });
    }
  }
  // This return true is essential for asynchronous message passing in Edge/Chrome
  return true; 
});