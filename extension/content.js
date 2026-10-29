// epoch 勤務実績入力画面に「活動履歴に同期」ボタンを足す。
// 入力処理（epoch_fill.js）は jQuery や画面側の関数を使うので、ページ側に差し込んで動かす。
// epoch の CSP は外部スクリプトを制限しているが 'unsafe-inline' は許可しているため、中身をインラインで差し込む。
const api = globalThis.browser ?? globalThis.chrome;
const firstDate = document.querySelector('input[name$=".DTJS_DT"]');

const injectFill = async () => {
  const response = await fetch(api.runtime.getURL("epoch_fill.js"));
  const script = document.createElement("script");
  script.textContent = await response.text();
  document.documentElement.appendChild(script);
};

// 画面に表示中の月（YYYY-MM）
const shownMonth = () => {
  const yyyymm = firstDate.value.slice(0, 6);
  return yyyymm.slice(0, 4) + "-" + yyyymm.slice(4);
};

// フッター帯の白い文字・アイコンと同じ扱いにして、epoch の画面になじませる。
// 押す前と押した後は白の濃さだけで区別する
const READY_STYLE = {
  border: "1px solid rgba(255, 255, 255, 0.85)",
  color: "#fff",
};

// 同期した後: もう押す必要はないので、さらに薄くして目立たなくする
const DONE_STYLE = {
  border: "1px solid rgba(255, 255, 255, 0.3)",
  color: "rgba(255, 255, 255, 0.55)",
};

// 同期マーク（2本の矢印の円）
const SYNC_ICON =
  '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
  'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex: none">' +
  '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3v5h5"/>' +
  '<path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 21v-5h-5"/></svg>';

const fill = async (button, label) => {
  const text = label.textContent;
  button.disabled = true;
  label.textContent = "活動履歴を取得中…";
  try {
    const result = await api.runtime.sendMessage({ type: "epoch-days", month: shownMonth() });
    if (result.error) {
      // ダイアログはページ側（epoch_fill.js の awDialog）で出す
      const dialog = {
        title: "活動履歴を取得できませんでした",
        message:
          "aw-work-hours サーバーに接続できませんでした。\n" +
          "ターミナルで aw-work-hours --html を起動してから、もう一度押してください。",
        details: [result.error],
      };
      document.dispatchEvent(new CustomEvent("aw-epoch-dialog", { detail: JSON.stringify(dialog) }));
      return;
    }
    document.dispatchEvent(new CustomEvent("aw-epoch-fill", { detail: JSON.stringify(result.days) }));
    Object.assign(button.style, DONE_STYLE);
  } finally {
    button.disabled = false;
    label.textContent = text;
  }
};

const addButton = () => {
  const button = document.createElement("button");
  button.type = "button";
  button.innerHTML = SYNC_ICON;
  const label = document.createElement("span");
  label.textContent = "活動履歴に同期";
  button.appendChild(label);
  // 表の上に重ならないよう、画面下の青いフッター帯（高さ約34px）の右寄りに収める。
  // 右端の「⇅」「?」アイコン（右から約80pxまで）を避ける
  Object.assign(button.style, {
    position: "fixed",
    right: "100px",
    bottom: "5px",
    zIndex: "10000",
    display: "flex",
    alignItems: "center",
    gap: "6px",
    height: "24px",
    padding: "0 12px",
    borderRadius: "4px",
    background: "transparent",
    fontFamily: "inherit",
    fontSize: "12px",
    cursor: "pointer",
    ...READY_STYLE,
  });
  button.addEventListener("click", () => fill(button, label));
  document.body.appendChild(button);
};

if (firstDate) {
  injectFill();
  addButton();
}
