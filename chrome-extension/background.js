// List of predefined domains
const predefinedDomains = ["mediaweb.ap.panopto.com"];

// Store tab information
let tabUrls = {};

// Function to check if the domain matches and execute a script
function checkDomainAndRunScript(url) {
  const domain = new URL(url).hostname;
  console.log(`domain: ${domain}`);
  if (predefinedDomains.includes(domain)) {
    console.log(`Matched domain: ${domain}`);
    runCustomScript(domain);
  }
}

function checkDomainAndCloseScript(tabId) {
  const url = tabUrls[tabId];
  if (!url) return; // Skip if no URL is stored for this tab

  const domain = new URL(url).hostname;
  console.log(`domain: ${domain}`);
  if (predefinedDomains.includes(domain)) {
    console.log(`Matched domain that was closed: ${domain}`);
    stopCustomScript(domain);
  }
}

// Define your custom script here
function runCustomScript(domain) {
  console.log(`Running script for: ${domain}`);
  fetch("http://0.0.0.0:1338/start")
}

function stopCustomScript(domain) {
  console.log(`Stopping script for: ${domain}`);
  fetch("http://0.0.0.0:1338/stop")
}

// Listen for tab updates (e.g., switching to a new tab or URL changes)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    tabUrls[tabId] = changeInfo.url; // Store the updated URL
    checkDomainAndRunScript(changeInfo.url);
  }
});

// Listen for tab closures
chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  console.log(`Tab with ID ${tabId} was closed.`);
  checkDomainAndCloseScript(tabId); // Use stored URL information
  delete tabUrls[tabId]; // Clean up stored data for the closed tab
});

// // Listen for navigation events (e.g., dynamic changes within a single-page app)
// chrome.webNavigation.onCompleted.addListener((details) => {
//   chrome.tabs.get(details.tabId, (tab) => {
//     if (tab.url) {
//       tabUrls[details.tabId] = tab.url; // Store the URL
//       checkDomainAndRunScript(tab.url);
//     }
//   });
// });
