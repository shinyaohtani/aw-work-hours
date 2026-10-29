// aw-work-hours: epoch 勤務実績入力画面の自動入力スクリプト
// 勤務実績入力画面の開発者ツールのコンソールに貼り付けて実行する。
// - 未登録の勤務日に、始業・終業・休憩（区分「休憩時間」）を入力する（サーバーには送らない）
// - 確認のうえ、事由「常時ＰＣ未使用者」を事由入力ダイアログ経由で登録する
// - 各行の「登録」ボタンは押さない。黄色の欄を確認してから自分で押すこと
(async () => {
  const DAYS = __AW_DAYS__;
  const REST_KIND = "12"; // 休憩時間
  const REASON = "Z0007"; // 常時ＰＣ未使用者
  const UNREGISTERED = "00";
  const WORKDAY = "01";

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const rowAt = (i) => $("#DATA_LIST tbody tr:eq(" + i + ")");
  const modal = () => document.querySelector("iframe.modalFrame");
  const colon = (hhmm) => hhmm.slice(0, 2) + ":" + hhmm.slice(2);

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
      } else if (row.find('[name="DTY_KB"]').val() !== WORKDAY) {
        skipped.push({ 日付: dt.value, 理由: "勤務日以外（AWに記録あり）" });
      } else {
        targets.push({ i, date: dt.value, day, row });
      }
    });
    return { targets, skipped };
  };

  // 手入力と同じく change / blur を発火させ、画面側の差時間計算や書式整形を走らせる
  const setTime = (row, cl, id, hhmm) => {
    const el = row.find("#" + cl + row.find("#" + cl).val()).children("#" + id)[0];
    if (!el || el.disabled) return false;
    el.value = colon(hhmm);
    el.dispatchEvent(new Event("change"));
    el.dispatchEvent(new Event("blur"));
    el.style.background = "#fff3b0";
    return true;
  };

  // 休憩/不就業変更入力ダイアログの「確定」が行に書き戻すのと同じ値を設定する
  const setBreaks = (t) => {
    const breaks = t.day.breaks;
    if (!breaks.length) return false;
    callbackClickRestFsjk({
      ROW_NO: t.i,
      KOB_REST_HEN_FL: "1",
      KOB_REST_DSP_HEN_FL: "1",
      KOB_REST_SKB_KB: breaks.map(() => REST_KIND).join(),
      KOB_REST_STTM: breaks.map((b) => b[0]).join(),
      KOB_REST_ETM: breaks.map((b) => b[1]).join(),
      KOB_REST_RY: breaks.map(() => "").join(),
      MEL_FL: t.row.find("#MEL_FL").val(),
    });
    t.row.find("#TM_CHG").css("background", "#fff3b0");
    return true;
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
  const report = targets.map((t) => ({
    日付: t.date,
    始業: setTime(t.row, "DTY_STH_CL", "DTY_STH", t.day.start) ? colon(t.day.start) : "入力不可",
    終業: setTime(t.row, "DTY_ENH_CL", "DTY_ENH", t.day.end) ? colon(t.day.end) : "入力不可",
    休憩: setBreaks(t)
      ? t.day.breaks.map((b) => colon(b[0]) + "-" + colon(b[1])).join(" ")
      : "なし（既定のまま）",
  }));
  console.log("aw-work-hours: 入力した日");
  console.table(report);
  if (skipped.length) {
    console.log("aw-work-hours: 入力しなかった日");
    console.table(skipped);
  }

  const reasonTargets = targets.filter(needsReason);
  const message =
    "事由「常時ＰＣ未使用者」を " + reasonTargets.length + " 日分登録します。\n" +
    "（勤務実績そのものの「登録」はまだ行いません）";
  if (reasonTargets.length && confirm(message)) {
    for (const t of reasonTargets) {
      try {
        await registerReason(t);
        console.log("aw-work-hours: 事由を登録しました", t.date);
      } catch (e) {
        console.error("aw-work-hours: 事由の登録で止まりました", t.date, e);
        alert(t.date + " の事由登録で止まりました。ダイアログを確認してください。");
        return;
      }
    }
  }
  alert(
    "aw-work-hours: " + report.length + " 日分を入力しました。\n" +
    "黄色の欄を確認してから、各行の「登録」を押してください。"
  );
})();
