let noColon = false;

function formatTime(h, m) {
    const sep = noColon ? '' : ':';
    return String(h).padStart(2, '0') + sep + String(m).padStart(2, '0');
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

function render(rows) {
    const table = document.getElementById('table');
    let html = '<tr class="hour-labels"><td></td><td></td><td></td><td></td><td><div>';
    for (let h = 0; h < 24; h += 4) html += `<span>${String(h).padStart(2,'0')}:00</span>`;
    html += '</div></td></tr>';
    for (const row of rows) {
        const holClass = row.holiday ? ' class="holiday"' : '';
        const holMark = row.holiday ? '*' : '';
        const dateCol = `${row.date} ${row.weekday}${holMark}`;
        let timeCol = '', durCol = '', afkCol = '';
        if (row.hasWork) {
            timeCol = `${formatTime(row.startH, row.startM)} - ${formatTime(row.endH, row.endM)}`;
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
