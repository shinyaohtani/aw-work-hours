// aw-work-hours サーバーから epoch 自動入力用の日程を取ってくる。
// https の epoch ページから http の localhost へは直接取りに行けないため、ここで仲介する。
const api = globalThis.browser ?? globalThis.chrome;
const SERVER = "http://127.0.0.1:8600";

api.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "epoch-days") return false;
  fetch(SERVER + "/epoch/" + message.month)
    .then((response) => {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then((body) => sendResponse({ days: body.days }))
    .catch((error) => sendResponse({ error: String(error) }));
  return true;
});
