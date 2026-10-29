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

// 押す前: epoch の青とは違うアプリだと分かるよう、黄色地に黒文字で目立たせる
const READY_STYLE = {
  border: "2px solid #1a1a1a",
  background: "#ffd60a",
  color: "#1a1a1a",
  fontWeight: "bold",
};

// 同期した後: もう押す必要はないので、フッター帯の青になじませて目立たなくする
const DONE_STYLE = {
  border: "1px solid rgba(255, 255, 255, 0.35)",
  background: "transparent",
  color: "rgba(255, 255, 255, 0.6)",
  fontWeight: "normal",
};

const fill = async (button) => {
  const label = button.textContent;
  button.disabled = true;
  button.textContent = "活動履歴を取得中…";
  try {
    const result = await api.runtime.sendMessage({ type: "epoch-days", month: shownMonth() });
    if (result.error) {
      alert(
        "aw-work-hours サーバーに接続できませんでした（" + result.error + "）。\n" +
        "ターミナルで aw-work-hours --html を起動してから、もう一度押してください。"
      );
      return;
    }
    document.dispatchEvent(new CustomEvent("aw-epoch-fill", { detail: JSON.stringify(result.days) }));
    Object.assign(button.style, DONE_STYLE);
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
};

const addButton = () => {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "活動履歴に同期";
  // 表の上に重ならないよう、画面下の青いフッター帯（高さ約34px）の右寄りに収める。
  // 右端の「⇅」「?」アイコン（右から約80pxまで）を避ける
  Object.assign(button.style, {
    position: "fixed",
    right: "100px",
    bottom: "4px",
    zIndex: "10000",
    height: "26px",
    padding: "0 16px",
    borderRadius: "13px",
    fontSize: "13px",
    lineHeight: "22px",
    cursor: "pointer",
    ...READY_STYLE,
  });
  button.addEventListener("click", () => fill(button));
  document.body.appendChild(button);
};

if (firstDate) {
  injectFill();
  addButton();
}
