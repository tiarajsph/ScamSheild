chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeText",
    title: "Analyze with ScamShield",
    contexts: ["selection"],
  });
  chrome.contextMenus.create({
    id: "scanQrImage",
    title: "Scan QR with ScamShield",
    contexts: ["image"],
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "analyzeText") {
    chrome.storage.local.set({ selectedText: info.selectionText }, () => {
      chrome.windows.create({
        url: "index.html",
        type: "normal",
        state: "maximized"
      });
    });
  } else if (info.menuItemId === "scanQrImage") {
    chrome.storage.local.set({ qrImageUrl: info.srcUrl }, () => {
      chrome.windows.create({
        url: "index.html?qrImage=1",
        type: "normal",
        state: "maximized"
      });
    });
  }
});
