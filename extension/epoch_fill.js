// aw-work-hours: epoch 勤務実績入力画面の自動入力
// epoch のページ内（jQuery や画面側の関数が見える場所）で動かす。
// - 拡張機能: content.js がこのファイルをページに差し込み、"aw-epoch-fill" イベントで日程を渡す
// - aw-work-hours --epoch: このファイルの末尾に awEpochFill(日程) の呼び出しを足してコンソールに貼る
//
// - 未登録の日を一覧で見せ、チェックした日にだけ始業・終業・休憩（区分「休憩時間」）を入力する（サーバーには送らない）
// - 「事由も登録する」にチェックがあれば、事由「常時ＰＣ未使用者」を事由入力ダイアログ経由で登録する
// - 各行の「登録」ボタンは押さない。黄色の欄を確認してから自分で押すこと
// aw-work-hours のダイアログ（ブラウザ標準の alert / confirm の代わり）。
// cancelLabel を渡すと確認ダイアログになり、OK なら true、キャンセルなら false を返す。
// checks（一覧の各行）や options（一覧の下）にチェックボックスを並べると、OK のとき
// { checks: [true/false...], options: [true/false...] } を返す
window.awDialog = ({
  title, message, details = [], checks = [], options = [], okLabel = "OK", cancelLabel = null,
}) =>
  new Promise((resolve) => {
    const font = '-apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", sans-serif';
    const overlay = document.createElement("div");
    Object.assign(overlay.style, {
      position: "fixed", inset: "0", zIndex: "2147483000", display: "flex",
      alignItems: "center", justifyContent: "center", background: "rgba(15, 23, 42, 0.45)",
      backdropFilter: "blur(2px)", fontFamily: font,
    });
    const card = document.createElement("div");
    Object.assign(card.style, {
      width: "min(440px, calc(100vw - 32px))", boxSizing: "border-box", padding: "24px",
      borderRadius: "14px", background: "#fff", color: "#1f2937",
      boxShadow: "0 24px 60px rgba(15, 23, 42, 0.3)",
    });
    card.innerHTML =
      '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">' +
      '<span style="display:flex;align-items:center;justify-content:center;width:28px;height:28px;' +
      'border-radius:8px;background:#0041c0;color:#fff;flex:none">' +
      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" ' +
      'stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 3v5h5"/>' +
      '<path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 21v-5h-5"/></svg></span>' +
      '<div data-part="title" style="font-size:16px;font-weight:600"></div></div>' +
      '<div data-part="message" style="font-size:14px;line-height:1.7;color:#4b5563;white-space:pre-wrap"></div>' +
      '<ul data-part="details" style="margin:12px 0 0;padding:10px 14px;list-style:none;max-height:220px;' +
      'overflow:auto;border-radius:8px;background:#f3f5f9;font-size:13px;line-height:1.8;color:#374151;' +
      'font-variant-numeric:tabular-nums"></ul>' +
      '<div data-part="options" style="margin-top:12px;font-size:13px;color:#374151"></div>' +
      '<div data-part="buttons" style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px"></div>';
    const part = (name) => card.querySelector('[data-part="' + name + '"]');
    part("title").textContent = title;
    part("message").textContent = message;
    const checkRow = (item, parent) => {
      const row = document.createElement(parent.tagName === "UL" ? "li" : "div");
      row.innerHTML =
        '<label style="display:flex;align-items:center;gap:8px;cursor:pointer">' +
        '<input type="checkbox" style="width:15px;height:15px;margin:0;accent-color:#0041c0;flex:none">' +
        "<span></span></label>";
      row.querySelector("input").checked = item.checked;
      row.querySelector("span").textContent = item.label;
      parent.appendChild(row);
      return row.querySelector("input");
    };
    details.forEach((line) => {
      const item = document.createElement("li");
      item.textContent = line;
      part("details").appendChild(item);
    });
    const checkBoxes = checks.map((item) => checkRow(item, part("details")));
    const optionBoxes = options.map((item) => checkRow(item, part("options")));
    if (!details.length && !checks.length) part("details").remove();
    if (!options.length) part("options").remove();
    const close = (answer) => {
      document.removeEventListener("keydown", onKey, true);
      overlay.remove();
      const checked = (boxes) => boxes.map((box) => box.checked);
      const withChecks = checks.length || options.length;
      resolve(answer && withChecks ? { checks: checked(checkBoxes), options: checked(optionBoxes) } : answer);
    };
    const addButton = (label, primary, answer) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      Object.assign(button.style, {
        minWidth: "88px", height: "34px", padding: "0 16px", borderRadius: "8px",
        fontFamily: font, fontSize: "14px", fontWeight: "600", cursor: "pointer",
        border: primary ? "1px solid #0041c0" : "1px solid #d1d5db",
        background: primary ? "#0041c0" : "#fff", color: primary ? "#fff" : "#374151",
      });
      button.addEventListener("click", () => close(answer));
      part("buttons").appendChild(button);
      return button;
    };
    const onKey = (event) => {
      if (event.key === "Escape") close(cancelLabel ? false : true);
      if (event.key === "Enter") close(true);
      if (event.key === "Escape" || event.key === "Enter") event.preventDefault();
    };
    if (cancelLabel) addButton(cancelLabel, false, false);
    const ok = addButton(okLabel, true, true);
    overlay.appendChild(card);
    document.body.appendChild(overlay);
    document.addEventListener("keydown", onKey, true);
    ok.focus();
  });

window.awEpochFill = async (DAYS) => {
  const REST_KIND = "12"; // 休憩時間
  const REASON = "Z0007"; // 常時ＰＣ未使用者
  const UNREGISTERED = "00";

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const rowAt = (i) => $("#DATA_LIST tbody tr:eq(" + i + ")");
  const modal = () => document.querySelector("iframe.modalFrame");
  const colon = (hhmm) => hhmm.slice(0, 2) + ":" + hhmm.slice(2);
  const dayLabel = (yyyymmdd) => {
    const d = new Date(+yyyymmdd.slice(0, 4), +yyyymmdd.slice(4, 6) - 1, +yyyymmdd.slice(6));
    return (d.getMonth() + 1) + "/" + d.getDate() + "（" + "日月火水木金土"[d.getDay()] + "）";
  };

  const waitFor = async (probe, ms = 15000) => {
    const deadline = Date.now() + ms;
    while (Date.now() < deadline) {
      const found = probe();
      if (found) return found;
      await sleep(200);
    }
    throw new Error("タイムアウトしました");
  };

  const targetDays = () => {
    const targets = [];
    const skipped = [];
    document.querySelectorAll('input[name$=".DTJS_DT"]').forEach((dt) => {
      const day = DAYS[dt.value];
      if (!day) return;
      const i = Number(dt.name.match(/\[(\d+)\]/)[1]);
      const row = rowAt(i);
      if (row.find("#DTJS_INPT_JKKB").val() !== UNREGISTERED) {
        skipped.push({ 日付: dt.value, 理由: "登録済・申請中" });
      } else {
        targets.push({ i, date: dt.value, day, row });
      }
    });
    return { targets, skipped };
  };

  // 手入力と同じく input / change / blur を発火させ、画面側の処理を走らせる
  // （input: 所定休日などの「登録」ボタン表示、change / blur: 差時間計算や書式整形）
  const setTime = (row, cl, id, hhmm) => {
    const el = row.find("#" + cl + row.find("#" + cl).val()).children("#" + id)[0];
    if (!el || el.disabled) return false;
    el.value = colon(hhmm);
    el.dispatchEvent(new Event("input"));
    el.dispatchEvent(new Event("change"));
    el.dispatchEvent(new Event("blur"));
    el.style.background = "#fff3b0";
    return true;
  };

  // 休憩/不就業変更入力ダイアログの「確定」が行に書き戻すのと同じ値を設定する。
  // 休憩がない日は、既定の休憩（12:00〜12:45 など）を全部「行削除」したときと同じ印を送って消す
  const REST_DELETED = [["99", "0000", "4759"]];
  const setBreaks = (t) => {
    const rests = t.day.breaks.length ? t.day.breaks.map((b) => [REST_KIND, b[0], b[1]]) : REST_DELETED;
    callbackClickRestFsjk({
      ROW_NO: t.i,
      KOB_REST_HEN_FL: "1",
      KOB_REST_DSP_HEN_FL: "1",
      KOB_REST_SKB_KB: rests.map((r) => r[0]).join(),
      KOB_REST_STTM: rests.map((r) => r[1]).join(),
      KOB_REST_ETM: rests.map((r) => r[2]).join(),
      KOB_REST_RY: rests.map(() => "").join(),
      MEL_FL: t.row.find("#MEL_FL").val(),
    });
    t.row.find("#TM_CHG").css("background", "#fff3b0");
  };

  const breaksLabel = (t) => (t.day.breaks.length ? "休憩 " + t.day.breaks.length + " 件" : "休憩なし");
  const dayKind = (t) => {
    const kind = t.row.find('[name="DPY_DTY_KBR"]').val();
    return kind && kind !== "勤務日" ? " " + kind : "";
  };

  const needsReason = (t) =>
    t.row.find("#NMN_JY_INPUT:visible:not([disabled])").length > 0 &&
    ["", "00000"].includes(t.row.find("#NMSJY_KB").val()) &&
    ["", "00000"].includes(t.row.find("#TMSJY_KB").val());

  const registerReason = async (t) => {
    clickNtisJiy(t.i);
    const win = await waitFor(() => {
      const frame = modal();
      const doc = frame && frame.contentDocument;
      const ready = doc && doc.readyState === "complete" && doc.getElementById("NMSJY_KB_LIST");
      return ready ? frame.contentWindow : null;
    });
    ["NMSJY_KB_LIST", "TMSJY_KB_LIST"].forEach((id) => {
      const select = win.document.getElementById(id);
      if (select && !select.disabled && !select.value) select.value = REASON;
    });
    win.doRegist();
    await waitFor(() => !modal());
  };

  const { targets, skipped } = targetDays();
  const skippedNote = skipped.length ? "\n登録済・申請中の " + skipped.length + " 日は対象外です。" : "";
  if (!targets.length) {
    await window.awDialog({ title: "活動履歴に同期", message: "入力できる日はありません。" + skippedNote });
    return false;
  }
  const choice = await window.awDialog({
    title: "活動履歴に同期",
    message: "チェックした日に、始業・終業・休憩を入力します。" + skippedNote,
    checks: targets.map((t) => ({
      label:
        dayLabel(t.date) + dayKind(t) + "　" + colon(t.day.start) + "–" + colon(t.day.end) + "　" + breaksLabel(t),
      checked: true,
    })),
    options: [{ label: "事由「常時ＰＣ未使用者」も登録する", checked: true }],
    okLabel: "入力する",
    cancelLabel: "キャンセル",
  });
  if (!choice) return false;
  const chosen = targets.filter((_, k) => choice.checks[k]);

  const report = chosen.map((t) => {
    const start = setTime(t.row, "DTY_STH_CL", "DTY_STH", t.day.start) ? colon(t.day.start) : "入力不可";
    const end = setTime(t.row, "DTY_ENH_CL", "DTY_ENH", t.day.end) ? colon(t.day.end) : "入力不可";
    setBreaks(t);
    return { 日付: t.date, 始業: start, 終業: end, 休憩: t.day.breaks.map((b) => colon(b[0]) + "-" + colon(b[1])).join(" ") || "なし" };
  });
  console.log("aw-work-hours: 入力した日");
  console.table(report);

  if (choice.options[0]) {
    for (const t of chosen.filter(needsReason)) {
      try {
        await registerReason(t);
        console.log("aw-work-hours: 事由を登録しました", t.date);
      } catch (e) {
        console.error("aw-work-hours: 事由の登録で止まりました", t.date, e);
        await window.awDialog({
          title: "事由の登録で止まりました",
          message: dayLabel(t.date) + " の事由を登録できませんでした。開いているダイアログを確認してください。",
        });
        return true;
      }
    }
  }
  await window.awDialog({
    title: "活動履歴を同期しました",
    message: chosen.length
      ? chosen.length + " 日分を入力しました。黄色の欄を確認してから、各行の「登録」を押してください。"
      : "チェックした日がないため、何も入力していません。",
    details: chosen.map((t, k) => dayLabel(t.date) + "　" + report[k].始業 + "–" + report[k].終業 + "　" + breaksLabel(t)),
  });
  return chosen.length > 0;
};

// 拡張機能（content.js）からの呼び出し口。日程は JSON 文字列で受け取る
// 終わったら "aw-epoch-result"（"done" = 入力した / "cancel" = 何もしなかった）で知らせる
document.addEventListener("aw-epoch-fill", async (event) => {
  const done = await window.awEpochFill(JSON.parse(event.detail));
  document.dispatchEvent(new CustomEvent("aw-epoch-result", { detail: done ? "done" : "cancel" }));
});

// 拡張機能（content.js）からのお知らせ。{ title, message, details } を JSON 文字列で受け取る
document.addEventListener("aw-epoch-dialog", (event) => {
  window.awDialog(JSON.parse(event.detail));
});
