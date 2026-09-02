let noColon = false;

function formatTime(h, m) {
    const sep = noColon ? '' : ':';
    return String(h).padStart(2, '0') + sep + String(m).padStart(2, '0');
}

function rawTime(h, m) {
    return String(h).padStart(2, '0') + String(m).padStart(2, '0');
}

let toastTimer = null;
function showToast(msg) {
    let el = document.getElementById('toast');
    if (!el) {
        el = document.createElement('div');
        el.id = 'toast';
        el.className = 'fixed left-1/2 -translate-x-1/2 bottom-8 px-4 py-2 rounded-md bg-gray-900 text-white text-sm shadow-lg opacity-0 transition-opacity duration-200 pointer-events-none z-[300]';
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.opacity = '1';
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.style.opacity = '0'; }, 1200);
}

async function copyTime(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (e) {
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (_) {}
        document.body.removeChild(ta);
    }
    showToast('時刻がクリップボードにコピーされました');
}

function formatDuration(sec) {
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return m >= 1 ? `${m}m ${s}s` : `${s}s`;
}

async function loadMonth(ym) {
    const status = document.getElementById('status');
    status.textContent = '読み込み中...';
    let data;
    try {
        const res = await fetch(`/data/${ym}`);
        data = await res.json();
    } catch (e) {
        status.textContent = 'エラー: データを取得できません';
        return;
    }
    status.textContent = `勤務: ${data.rows.filter(r => r.hasWork).length}日`;
    render(data.rows);
}

let lastRows = [];

function render(rows) {
    lastRows = rows;
    const table = document.getElementById('table');
    let html = '<tr class="hour-labels"><td></td><td></td><td></td><td></td><td><div>';
    for (let h = 0; h < 24; h += 4) html += `<span>${String(h).padStart(2,'0')}:00</span>`;
    html += '</div></td></tr>';
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const holClass = row.holiday ? ' class="holiday"' : '';
        const holMark = row.holiday ? '*' : '';
        const dateCol = `${row.date} ${row.weekday}${holMark}`;
        let timeCol = '', durCol = '', afkCol = '';
        if (row.hasWork) {
            const startRaw = rawTime(row.startH, row.startM);
            const endRaw = rawTime(row.endH, row.endM);
            const hasBreaks = row.breaks && row.breaks.length;
            const breakIcon = `<span class="break-icon ml-1 ${hasBreaks ? 'cursor-pointer' : 'invisible'}" data-row="${i}" title="休憩を見る">☕</span>`;
            timeCol = `<span class="time-copy cursor-pointer hover:bg-yellow-100 rounded px-0.5" data-copy="${startRaw}">${formatTime(row.startH, row.startM)}</span> - <span class="time-copy cursor-pointer hover:bg-yellow-100 rounded px-0.5" data-copy="${endRaw}">${formatTime(row.endH, row.endM)}</span>${breakIcon}`;
            durCol = `(${row.span.toFixed(1)}h)`;
            if (row.afk !== undefined) afkCol = `-${row.afk.toFixed(1)}h (max:-${row.maxGap.toFixed(1)}h)`;
        }
        const hourMarks = [4,8,12,16,20].map(h => `<div class="hour-mark" style="left:${(h/24)*100}%"></div>`).join('');
        let eventBars = '';
        for (const ev of row.events || []) {
            const startSec = ev.startH * 3600 + ev.startM * 60 + ev.startS;
            const endSec = ev.endH * 3600 + ev.endM * 60 + ev.endS;
            const left = (startSec / 86400) * 100;
            const width = Math.max(0.1, ((endSec - startSec) / 86400) * 100);
            const startTime = `${String(ev.startH).padStart(2,'0')}:${String(ev.startM).padStart(2,'0')}:${String(ev.startS).padStart(2,'0')}`;
            const endTime = `${String(ev.endH).padStart(2,'0')}:${String(ev.endM).padStart(2,'0')}:${String(ev.endS).padStart(2,'0')}`;
            eventBars += `<div class="event" style="left:${left.toFixed(2)}%;width:${width.toFixed(2)}%;">
<div class="tooltip">
<div class="tooltip-row"><span class="tooltip-label">Start</span>${startTime}</div>
<div class="tooltip-row"><span class="tooltip-label">Stop</span>${endTime}</div>
<div class="tooltip-row"><span class="tooltip-label">Duration</span>${formatDuration(ev.duration)}</div>
<div class="tooltip-row"><span class="tooltip-label">Data</span>${JSON.stringify(ev.data)}</div>
</div></div>`;
        }
        html += `<tr${holClass}><td class="date">${dateCol}</td><td class="time">${timeCol}</td><td class="dur">${durCol}</td><td class="afk">${afkCol}</td><td class="timeline-cell"><div class="timeline"><div class="hour-marks">${hourMarks}</div>${eventBars}</div></td></tr>`;
    }
    table.innerHTML = html;
    document.querySelectorAll('.time-copy').forEach(el => {
        el.addEventListener('click', () => copyTime(el.dataset.copy));
    });
    document.querySelectorAll('.break-icon').forEach(el => {
        const row = lastRows[el.dataset.row];
        if (row.breaks && row.breaks.length) {
            el.addEventListener('click', () => openBreaks(row, el));
        }
    });
    document.querySelectorAll('.event').forEach(el => {
        const tooltip = el.querySelector('.tooltip');
        el.addEventListener('mouseenter', () => {
            tooltip.style.display = 'block';
            tooltip.style.top = '22px';
            tooltip.style.left = '0px';
            tooltip.style.right = 'auto';
            const rect = tooltip.getBoundingClientRect();
            if (rect.right > window.innerWidth) { tooltip.style.left = 'auto'; tooltip.style.right = '0px'; }
        });
        el.addEventListener('mouseleave', () => tooltip.style.display = 'none');
    });
}

// Break overlay
const breakOverlay = document.getElementById('break-overlay');
const breakPanel = document.getElementById('break-panel');
const breakList = document.getElementById('break-list');
const breakDate = document.getElementById('break-date');
const breakWorkSpan = document.getElementById('break-work-span');

function breakRowHtml(b) {
    const startRaw = rawTime(b.startH, b.startM);
    const endRaw = rawTime(b.endH, b.endM);
    const mins = (b.endH * 60 + b.endM) - (b.startH * 60 + b.startM);
    return `<div class="break-row flex items-center gap-2 px-3 py-2 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors">
<span class="time-copy cursor-pointer rounded px-1 font-medium text-gray-800 hover:bg-amber-100 hover:text-amber-800" data-copy="${startRaw}">${formatTime(b.startH, b.startM)}</span>
<span class="break-arrow text-gray-300">&rarr;</span>
<span class="time-copy cursor-pointer rounded px-1 font-medium text-gray-800 hover:bg-amber-100 hover:text-amber-800" data-copy="${endRaw}">${formatTime(b.endH, b.endM)}</span>
<span class="text-[11px] text-gray-400 ml-auto">${mins}分</span>
</div>`;
}

function openBreaks(row, anchorEl) {
    const holMark = row.holiday ? '*' : '';
    breakDate.textContent = `${row.date} ${row.weekday}${holMark}`;
    breakWorkSpan.textContent = `${formatTime(row.startH, row.startM)} - ${formatTime(row.endH, row.endM)}`;
    breakList.innerHTML = row.breaks.map(breakRowHtml).join('');
    breakList.querySelectorAll('.time-copy').forEach(el => {
        el.addEventListener('click', () => copyTime(el.dataset.copy));
    });
    breakOverlay.classList.remove('hidden');
    positionBreakPanel(anchorEl);
}

function positionBreakPanel(anchorEl) {
    const margin = 8;
    const anchor = anchorEl.getBoundingClientRect();
    breakPanel.style.visibility = 'hidden';
    breakPanel.style.top = '0px';
    breakPanel.style.left = '0px';
    const panel = breakPanel.getBoundingClientRect();

    let top = anchor.bottom + margin;
    let arrowClass = 'arrow-top';
    if (top + panel.height > window.innerHeight - margin) {
        top = anchor.top - panel.height - margin;
        arrowClass = 'arrow-bottom';
    }
    top = Math.max(margin, top);

    let left = anchor.left + anchor.width / 2 - panel.width / 2;
    left = Math.min(Math.max(left, margin), window.innerWidth - panel.width - margin);

    let arrowLeft = anchor.left + anchor.width / 2 - left;
    arrowLeft = Math.min(Math.max(arrowLeft, 14), panel.width - 14);

    breakPanel.style.setProperty('--arrow-left', `${arrowLeft}px`);
    breakPanel.classList.remove('arrow-top', 'arrow-bottom');
    breakPanel.classList.add(arrowClass);
    breakPanel.style.top = `${top}px`;
    breakPanel.style.left = `${left}px`;
    breakPanel.style.visibility = 'visible';
}

function hideBreaks() {
    breakOverlay.classList.add('hidden');
}

breakOverlay.addEventListener('click', e => { if (e.target === breakOverlay) hideBreaks(); });
document.getElementById('break-close').addEventListener('click', hideBreaks);
document.getElementById('break-done').addEventListener('click', hideBreaks);

function changeMonth(delta) {
    const input = document.getElementById('month');
    const [y, m] = input.value.split('-').map(Number);
    const d = new Date(y, m - 1 + delta, 1);
    input.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    loadMonth(input.value);
}

// Settings dialog
const overlay = document.getElementById('settings-overlay');

function hideDialog() {
    overlay.classList.add('hidden');
}

async function openSettings() {
    overlay.classList.remove('hidden');
    try {
        const [settingsRes, bucketsRes] = await Promise.all([
            fetch('/settings'), fetch('/settings/buckets')
        ]);
        const settings = await settingsRes.json();
        const buckets = await bucketsRes.json();
        document.getElementById('s-no-colon').checked = settings.no_colon;
        document.getElementById('s-min-event').value = settings.min_event_seconds;
        const sel = document.getElementById('s-bucket');
        sel.innerHTML = '<option value="">自動選択</option>';
        for (const h of buckets) {
            const opt = document.createElement('option');
            opt.value = h;
            opt.textContent = h;
            if (settings.bucket === h) opt.selected = true;
            sel.appendChild(opt);
        }
    } catch (e) {
        // ignore load errors
    }
}

async function saveSettings() {
    const body = {
        no_colon: document.getElementById('s-no-colon').checked,
        min_event_seconds: parseInt(document.getElementById('s-min-event').value, 10),
        bucket: document.getElementById('s-bucket').value || null
    };
    try {
        const res = await fetch('/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        const saved = await res.json();
        noColon = saved.no_colon;
        document.getElementById('noColon').checked = noColon;
        hideDialog();
        loadMonth(document.getElementById('month').value);
    } catch (e) {
        alert('設定の保存に失敗しました');
    }
}

// Event listeners
document.getElementById('prev').addEventListener('click', () => changeMonth(-1));
document.getElementById('next').addEventListener('click', () => changeMonth(1));
document.getElementById('month').addEventListener('change', e => loadMonth(e.target.value));
document.getElementById('noColon').addEventListener('change', e => {
    noColon = e.target.checked;
    loadMonth(document.getElementById('month').value);
});
document.getElementById('settings-btn').addEventListener('click', openSettings);
document.getElementById('s-cancel').addEventListener('click', hideDialog);
document.getElementById('s-save').addEventListener('click', saveSettings);
overlay.addEventListener('click', e => { if (e.target === overlay) hideDialog(); });

// Init
async function init() {
    // Load settings from API
    try {
        const res = await fetch('/settings');
        const settings = await res.json();
        noColon = settings.no_colon;
        document.getElementById('noColon').checked = noColon;
    } catch (e) {
        // use defaults
    }

    // Determine initial month from URL or current date
    const params = new URLSearchParams(window.location.search);
    const now = new Date();
    const initMonth = params.get('month') || `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    document.getElementById('month').value = initMonth;
    loadMonth(initMonth);
}

init();
