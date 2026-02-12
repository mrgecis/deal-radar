/* ─── Certina AI Deal Agent – App Logic (Premium Financial UI) ──────────────── */

// ── EMBEDDED DATA (No API calls needed!) ──────────────────────────────────
// All data is hardcoded for offline/Netlify deployment
const EMBEDDED_COMPANIES = [{"company_id": "atos", "name": "Atos SE", "year": "unknown", "score": 9, "hit_types": ["biz_services", "carve_out", "external_revenue", "loss_stress"], "hit_count": 505, "pdfs": [{"year": "unknown", "filename": "atos_unknown_9863907a.pdf", "url": "/pdfs/atos/unknown/atos_unknown_9863907a.pdf", "size_kb": 453}, {"year": "unknown", "filename": "atos_unknown_a642f2d9.pdf", "url": "/pdfs/atos/unknown/atos_unknown_a642f2d9.pdf", "size_kb": 2570}, {"year": "unknown", "filename": "atos_unknown_fce27ec7.pdf", "url": "/pdfs/atos/unknown/atos_unknown_fce27ec7.pdf", "size_kb": 1603}, {"year": "2025", "filename": "atos_2025_c4d69a2d.pdf", "url": "/pdfs/atos/2025/atos_2025_c4d69a2d.pdf", "size_kb": 24706}, {"year": "2025", "filename": "atos_2025_9e08a4f2.pdf", "url": "/pdfs/atos/2025/atos_2025_9e08a4f2.pdf", "size_kb": 1762}, {"year": "2024", "filename": "atos_2024_ff2285f1.pdf", "url": "/pdfs/atos/2024/atos_2024_ff2285f1.pdf", "size_kb": 304}, {"year": "2024", "filename": "atos_2024_05f0cf3d.pdf", "url": "/pdfs/atos/2024/atos_2024_05f0cf3d.pdf", "size_kb": 2954}, {"year": "2024", "filename": "atos_2024_1e990bb0.pdf", "url": "/pdfs/atos/2024/atos_2024_1e990bb0.pdf", "size_kb": 692}, {"year": "2024", "filename": "atos_2024_8d3fb059.pdf", "url": "/pdfs/atos/2024/atos_2024_8d3fb059.pdf", "size_kb": 4659}, {"year": "2023", "filename": "atos_2023_5cd4acb0.pdf", "url": "/pdfs/atos/2023/atos_2023_5cd4acb0.pdf", "size_kb": 643}, {"year": "2023", "filename": "atos_2023_9bd84113.pdf", "url": "/pdfs/atos/2023/atos_2023_9bd84113.pdf", "size_kb": 6790}, {"year": "2022", "filename": "atos_2022_cfd2141e.pdf", "url": "/pdfs/atos/2022/atos_2022_cfd2141e.pdf", "size_kb": 8826}, {"year": "2022", "filename": "atos_2022_42c9762a.pdf", "url": "/pdfs/atos/2022/atos_2022_42c9762a.pdf", "size_kb": 1234}, {"year": "2021", "filename": "atos_2021_cffadc88.pdf", "url": "/pdfs/atos/2021/atos_2021_cffadc88.pdf", "size_kb": 10323}, {"year": "2021", "filename": "atos_2021_4a9d6897.pdf", "url": "/pdfs/atos/2021/atos_2021_4a9d6897.pdf", "size_kb": 1226}, {"year": "2020", "filename": "atos_2020_fec3acd3.pdf", "url": "/pdfs/atos/2020/atos_2020_fec3acd3.pdf", "size_kb": 1894}, {"year": "2020", "filename": "atos_2020_6bd468c5.pdf", "url": "/pdfs/atos/2020/atos_2020_6bd468c5.pdf", "size_kb": 1139}, {"year": "2019", "filename": "atos_2019_7282af3b.pdf", "url": "/pdfs/atos/2019/atos_2019_7282af3b.pdf", "size_kb": 8487}], "score_breakdown": [{"type": "carve_out", "label": "Carve-out / Divestment", "count": 193, "weight": 3}, {"type": "loss_stress", "label": "Verlust / Financial Distress", "count": 85, "weight": 3}, {"type": "external_revenue", "label": "Externe Umsaetze", "count": 59, "weight": 2}, {"type": "biz_services", "label": "Business Services (extern)", "count": 168, "weight": 1}], "yearly_scores": [{"year": "2019", "score": 9}, {"year": "2020", "score": 9}, {"year": "2021", "score": 9}, {"year": "2022", "score": 9}, {"year": "2023", "score": 9}, {"year": "2024", "score": 9}, {"year": "2025", "score": 9}]}, {"company_id": "fujitsu", "name": "Fujitsu Limited", "year": "unknown", "score": 7, "hit_types": ["biz_services", "carve_out", "external_revenue", "loss_stress"], "hit_count": 30, "pdfs": [{"year": "unknown", "filename": "fujitsu_unknown_70e4e930.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_70e4e930.pdf", "size_kb": 99}, {"year": "unknown", "filename": "fujitsu_unknown_5f4f1901.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_5f4f1901.pdf", "size_kb": 627}, {"year": "unknown", "filename": "fujitsu_unknown_0fc6e00b.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_0fc6e00b.pdf", "size_kb": 272}, {"year": "unknown", "filename": "fujitsu_unknown_a1952011.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_a1952011.pdf", "size_kb": 62}, {"year": "unknown", "filename": "fujitsu_unknown_22719aa0.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_22719aa0.pdf", "size_kb": 161}, {"year": "unknown", "filename": "fujitsu_unknown_35345eb2.pdf", "url": "/pdfs/fujitsu/unknown/fujitsu_unknown_35345eb2.pdf", "size_kb": 169}, {"year": "2012", "filename": "fujitsu_2012_2bf07636.pdf", "url": "/pdfs/fujitsu/2012/fujitsu_2012_2bf07636.pdf", "size_kb": 160}, {"year": "2012", "filename": "fujitsu_2012_b7f7fb43.pdf", "url": "/pdfs/fujitsu/2012/fujitsu_2012_b7f7fb43.pdf", "size_kb": 1127}, {"year": "2010", "filename": "fujitsu_2010_17508042.pdf", "url": "/pdfs/fujitsu/2010/fujitsu_2010_17508042.pdf", "size_kb": 265}, {"year": "2010", "filename": "fujitsu_2010_76feb161.pdf", "url": "/pdfs/fujitsu/2010/fujitsu_2010_76feb161.pdf", "size_kb": 52}], "score_breakdown": [{"type": "carve_out", "label": "Carve-out / Divestment", "count": 9, "weight": 3}, {"type": "loss_stress", "label": "Verlust / Financial Distress", "count": 11, "weight": 3}, {"type": "external_revenue", "label": "Externe Umsaetze", "count": 3, "weight": 2}, {"type": "biz_services", "label": "Business Services (extern)", "count": 7, "weight": 1}], "yearly_scores": [{"year": "2012", "score": 9}]}, {"company_id": "deutsche_telekom", "name": "Deutsche Telekom AG", "year": "unknown", "score": 6, "hit_types": ["biz_services", "carve_out", "external_revenue", "loss_stress"], "hit_count": 68, "pdfs": [{"year": "unknown", "filename": "deutsche_telekom_unknown_ca555cb7.pdf", "url": "/pdfs/deutsche_telekom/unknown/deutsche_telekom_unknown_ca555cb7.pdf", "size_kb": 407}, {"year": "unknown", "filename": "deutsche_telekom_unknown_489f4419.pdf", "url": "/pdfs/deutsche_telekom/unknown/deutsche_telekom_unknown_489f4419.pdf", "size_kb": 322}, {"year": "unknown", "filename": "deutsche_telekom_unknown_2fd1a45f.pdf", "url": "/pdfs/deutsche_telekom/unknown/deutsche_telekom_unknown_2fd1a45f.pdf", "size_kb": 2312}, {"year": "2016", "filename": "deutsche_telekom_2016_ecd56f06.pdf", "url": "/pdfs/deutsche_telekom/2016/deutsche_telekom_2016_ecd56f06.pdf", "size_kb": 3002}, {"year": "2013", "filename": "deutsche_telekom_2013_45ca4d88.pdf", "url": "/pdfs/deutsche_telekom/2013/deutsche_telekom_2013_45ca4d88.pdf", "size_kb": 49}, {"year": "2012", "filename": "deutsche_telekom_2012_06bb4704.pdf", "url": "/pdfs/deutsche_telekom/2012/deutsche_telekom_2012_06bb4704.pdf", "size_kb": 4195}, {"year": "2010", "filename": "deutsche_telekom_2010_d47205ac.pdf", "url": "/pdfs/deutsche_telekom/2010/deutsche_telekom_2010_d47205ac.pdf", "size_kb": 2660}], "score_breakdown": [{"type": "loss_stress", "label": "Verlust / Financial Distress", "count": 10, "weight": 3}, {"type": "carve_out", "label": "Carve-out / Divestment", "count": 27, "weight": 3}, {"type": "external_revenue", "label": "Externe Umsaetze", "count": 12, "weight": 2}, {"type": "biz_services", "label": "Business Services (extern)", "count": 19, "weight": 1}], "yearly_scores": [{"year": "2010", "score": 6}, {"year": "2012", "score": 9}, {"year": "2013", "score": 3}]}, {"company_id": "cgi", "name": "CGI Inc.", "year": "2026", "score": 2, "hit_types": ["biz_services", "carve_out", "external_revenue", "loss_stress"], "hit_count": 405, "pdfs": [{"year": "2026", "filename": "cgi_2026_93aa4535.pdf", "url": "/pdfs/cgi/2026/cgi_2026_93aa4535.pdf", "size_kb": 85}, {"year": "2025", "filename": "cgi_2025_9df20e93.pdf", "url": "/pdfs/cgi/2025/cgi_2025_9df20e93.pdf", "size_kb": 3475}], "score_breakdown": [{"type": "carve_out", "label": "Carve-out / Divestment", "count": 129, "weight": 3}, {"type": "loss_stress", "label": "Verlust / Financial Distress", "count": 45, "weight": 3}, {"type": "external_revenue", "label": "Externe Umsaetze", "count": 104, "weight": 2}, {"type": "biz_services", "label": "Business Services (extern)", "count": 127, "weight": 1}], "yearly_scores": [{"year": "2018", "score": 9}, {"year": "2019", "score": 9}, {"year": "2020", "score": 9}, {"year": "2021", "score": 9}, {"year": "2022", "score": 9}, {"year": "2023", "score": 9}, {"year": "2024", "score": 9}, {"year": "2025", "score": 9}, {"year": "2026", "score": 2}]}];

const EMBEDDED_STATS = {"companies": 4, "pdfs": 207, "signals": 1008, "chunks": 13111, "avg_score": 8.1};

// ── API Configuration ──────────────────────────────────────────────────────
// For local development: http://localhost:8000
// For production: set via environment variable or update directly
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : (window.__API_BASE_URL__ || '');

const HIT_TYPE_LABELS = {
  carve_out: 'Carve-out / Divestment',
  loss_stress: 'Financial Distress',
  biz_services: 'Business Services',
  external_revenue: 'External Revenue',
};

let companies = [];

// ── Icons (SVG Helpers) ── 
const Icons = {
  up: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15"></polyline></svg>',
  down: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9"></polyline></svg>',
  pdf: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
};

// ── View Management ────────────────────────────────────────────────────────

function showDashboard() {
  document.querySelectorAll('.main-content').forEach(m => m.classList.add('hidden'));
  document.getElementById('dashboard-view').classList.remove('hidden');
  updateNavActive(0);
}

function showCompaniesTab() {
  document.querySelectorAll('.main-content').forEach(m => m.classList.add('hidden'));
  document.querySelector('.companies-view').classList.remove('hidden');
  updateNavActive(1);
  document.getElementById('search-intelligence').focus();
}

function updateNavActive(index) {
  // Desktop Sidebar
  document.querySelectorAll('.nav-item').forEach((item, i) => {
    item.classList.toggle('active', i === index);
  });
  // Mobile Bottom Nav
  document.querySelectorAll('.mobile-nav-item').forEach((item, i) => {
    item.classList.toggle('active', i === index);
  });
}

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  // Set Date
  const dateOpts = { weekday: 'long', month: 'long', day: 'numeric' };
  document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', dateOpts);
  document.getElementById('companies-date').textContent = new Date().toLocaleDateString('en-US', dateOpts);

  try {
    // Use embedded data instead of API calls
    companies = EMBEDDED_COMPANIES;
    const stats = EMBEDDED_STATS;

    renderGrid(companies);
    renderKpis(stats);
    document.getElementById('opp-count').textContent = companies.length;

  } catch (e) {
    console.error('Error loading data:', e);
    document.getElementById('company-grid').innerHTML =
      '<div style="text-align:center;color:var(--text-secondary);grid-column:1/-1;padding:40px;">Unable to load data. Ensure server is running.</div>';
  }

  const loader = document.getElementById('loading');
  if (loader) loader.style.display = 'none';

  document.getElementById('search').addEventListener('input', applyFilters);
  document.getElementById('filter-type').addEventListener('change', applyFilters);
});

// ── KPI Rendering ────────────────────────────────────────────────────────────
function renderKpis(s) {
  const kpiMap = [
    { label: 'Pipeline', val: s.companies, trend: 'neutral' },
    { label: 'Signals', val: s.signals.toLocaleString(), trend: 'up' },
    { label: 'Reports', val: s.pdfs.toLocaleString(), trend: 'neutral' },
    { label: 'Avg Score', val: s.avg_score, trend: s.avg_score > 5 ? 'up' : 'neutral' },
  ];

  document.getElementById('kpi-bar').innerHTML = kpiMap.map(k => `
    <div class="kpi-card">
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value">${k.val}</div>
      <div class="kpi-trend ${k.trend === 'up' ? 'trend-up' : 'trend-neutral'}">
        ${k.trend === 'up' ? Icons.up + ' +12% this week' : 'Stable'}
      </div>
    </div>
  `).join('');
}

// ── Grid Rendering ───────────────────────────────────────────────────────────
function renderGrid(data) {
  const grid = document.getElementById('company-grid');
  document.getElementById('opp-count').textContent = data.length;

  if (!data.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-secondary);">No companies match your filters.</div>';
    return;
  }

  grid.innerHTML = data.map(c => {
    let scoreClass = 'score-low';
    if (c.score >= 7) scoreClass = 'score-high';
    else if (c.score >= 4) scoreClass = 'score-med';

    const tags = c.hit_types.map(t =>
      `<span class="tag ${t}">${HIT_TYPE_LABELS[t]?.split('/')[0] || t}</span>`
    ).join('');

    const pdfInfo = c.pdfs && c.pdfs.length
      ? `<span class="pdf-pill">${Icons.pdf} ${c.pdfs.length} Reports</span>`
      : '';

    return `
      <div class="company-card" onclick="openDetail('${c.company_id}')">
        <div class="card-header">
          <div>
            <h3>${c.name}</h3>
          </div>
          <div class="score-indicator ${scoreClass}">${c.score}</div>
        </div>
        <div class="card-meta">Latest Report: ${c.year}</div>
        <div class="card-tags">${tags}</div>
        <div class="card-footer">
          <span class="hit-count">${c.hit_count} Signals Detected</span>
          ${pdfInfo}
        </div>
      </div>
    `;
  }).join('');
}

// ── Filters ──────────────────────────────────────────────────────────────────
function applyFilters() {
  const q = document.getElementById('search').value.toLowerCase();
  const type = document.getElementById('filter-type').value;

  const filtered = companies.filter(c => {
    const matchName = c.name.toLowerCase().includes(q) || c.company_id.includes(q);
    const matchType = !type || c.hit_types.includes(type);
    return matchName && matchType;
  });
  renderGrid(filtered);
}




// ── Detail Modal ─────────────────────────────────────────────────────────────
async function openDetail(companyId) {
  const modal = document.getElementById('modal');
  const title = document.getElementById('modal-title');
  const body = document.getElementById('modal-content');

  const c = companies.find(x => x.company_id === companyId);
  if (!c) return;

  title.textContent = c.name;

  // Skeleton / Loading state logic could go here
  body.innerHTML = `
    <div class="section-block">
      <div class="section-title">Score Breakdown</div>
      <div style="display:flex; gap:12px; margin-bottom:12px;">
         ${(c.score_breakdown || []).map(b => `
            <div style="flex:1; background:var(--surface-1); padding:8px; border-radius:8px; border:1px solid var(--surface-3);">
              <div style="font-size:11px; color:var(--text-secondary); margin-bottom:4px;">${b.label}</div>
              <div style="font-size:14px; font-weight:600;">${b.count}</div>
            </div>
         `).join('')}
      </div>
    </div>

    <div class="section-block" id="report-actions">
       <div class="section-title">AI Actions</div>
       <div class="action-row">
         <button class="btn-primary" onclick="generateReport('${companyId}')">Generate AI Report</button>
         <button class="btn-secondary" onclick="checkRelevance('${companyId}')">Check Source Relevance</button>
       </div>
       <div id="ai-output" style="margin-top:16px;"></div>
    </div>

    <div class="section-block">
       <div class="section-title">Evidence & Signals</div>
       <div id="evidence-container">
         <div class="loading-state" style="margin:0;"><div class="spinner" style="width:16px;height:16px;border-width:2px;"></div></div>
       </div>
    </div>

    <div class="section-block">
      <div class="section-title">Source Documents</div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        ${(c.pdfs || []).map(p => `
          <a href="${p.url}" target="_blank" style="background:var(--surface-1); padding:10px; border-radius:8px; text-decoration:none; display:flex; align-items:center; gap:8px; border:1px solid var(--surface-3);">
             ${Icons.pdf}
             <div style="overflow:hidden;">
               <div style="font-size:12px; color:var(--text-primary); font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.filename}</div>
               <div style="font-size:10px; color:var(--text-secondary);">${p.year} • ${p.size_kb} KB</div>
             </div>
          </a>
        `).join('')}
      </div>
    </div>
  `;

  modal.classList.remove('hidden');

  // Load Evidence
  try {
    const res = await fetch(API_BASE_URL + '/api/evidence?company=' + companyId);
    const evidence = await res.json();
    renderEvidence(evidence, c.name);
  } catch (e) {
    document.getElementById('evidence-container').innerHTML = '<div style="font-size:13px; color:var(--text-secondary);">Failed to load evidence.</div>';
    console.error(e);
  }
}

function renderEvidence(ev, companyName) {
  const container = document.getElementById('evidence-container');

  // Backend returns a dictionary grouped by hit_type, e.g. {"carve_out": [...], "loss_stress": [...]}
  if (!ev || typeof ev !== 'object' || Object.keys(ev).length === 0) {
    container.innerHTML = `<p style="text-align:center;color:var(--text-secondary);">No specific evidence found for ${companyName}.</p>`;
    return;
  }

  let html = '';

  // Iterate through each hit type
  for (const [hitType, items] of Object.entries(ev)) {
    const typeLabel = HIT_TYPE_LABELS[hitType] || hitType;

    items.forEach(item => {
      // Highlight the keyword in the snippet
      let snippet = item.snippet || '';
      const keyword = item.keyword || '';

      if (keyword) {
        // Escape special regex characters in keyword
        const escapedKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const pattern = new RegExp(`(${escapedKeyword})`, 'gi');
        snippet = snippet.replace(pattern, '<mark>$1</mark>');
      }

      html += `
        <div class="evidence-card">
          <div class="evidence-kw">${typeLabel}</div>
          <div class="evidence-text">"${snippet}"</div>
          <div class="evidence-src">
            <span>${item.source_file} (${item.year})</span>
            ${item.pdf_url ? `
              &bull; <a href="${item.pdf_url}" target="_blank" class="pdf-link">View PDF</a>
            ` : ''}
          </div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
}

function closeModal() {
  document.getElementById('modal').classList.add('hidden');
}

// ── AI Actions ───────────────────────────────────────────────────────────────
async function checkRelevance(companyId) {
  const output = document.getElementById('ai-output');
  output.innerHTML = '<div style="font-size:13px;color:var(--text-secondary);">AI is analyzing signal relevance...</div>';

  try {
    const res = await fetch(API_BASE_URL + '/api/relevance?company=' + companyId);
    const data = await res.json();

    // Simple verification result
    output.innerHTML = `
      <div style="background:var(--surface-1); padding:12px; border-radius:8px; border:1px solid var(--glass-border);">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
           <span style="font-weight:600;">Confidence Score</span>
           <span style="${data.adjusted_score < data.original_score ? 'color:var(--red);' : 'color:var(--green);'}">${data.original_score} → ${data.adjusted_score}</span>
        </div>
        <div style="font-size:12px; color:var(--text-secondary);">
           Analyzed ${data.total_signals} signals. Found ${data.false_positives} potential false positives.
        </div>
      </div>
    `;
  } catch (e) {
    output.innerHTML = '<div style="color:var(--red); font-size:13px;">Analysis failed.</div>';
  }
}

async function generateReport(companyId) {
  const output = document.getElementById('ai-output');
  output.innerHTML = '<div style="font-size:13px;color:var(--text-secondary);">Generating executive summary...</div>';

  try {
    const res = await fetch(API_BASE_URL + '/api/report?company=' + companyId);
    const data = await res.json();

    output.innerHTML = `
      <div style="background:var(--surface-1); padding:16px; border-radius:12px; border:1px solid var(--glass-border); margin-top:12px;">
         <h4 style="margin:0 0 12px 0; font-size:14px;">Executive AI Report</h4>
         <div style="font-size:13px; line-height:1.6; color:var(--text-secondary); white-space:pre-wrap;">${data.report}</div>
      </div>
    `;
  } catch (e) {
    output.innerHTML = '<div style="color:var(--red); font-size:13px;">Report generation failed.</div>';
  }
}

// ── Chat ─────────────────────────────────────────────────────────────────────
function toggleChat() {
  document.getElementById('chat-panel').classList.toggle('hidden');
}

async function sendChat(event) {
  event.preventDefault();
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  appendMsg('user', msg);
  input.value = '';

  const loadingId = appendMsg('bot', 'Analyzing...');

  try {
    const res = await fetch(API_BASE_URL + '/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();

    // Replace loading
    document.getElementById(loadingId).remove();
    appendMsg('bot', data.answer);

  } catch (e) {
    document.getElementById(loadingId).innerText = "Error connecting to Analyst.";
  }
}

function appendMsg(role, text) {
  const box = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.id = 'msg-' + Date.now();
  div.innerHTML = `<div class="bubble">${text}</div>`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div.id;
}


/* ─── Add Company Functions ─────────────────────────────────────────── */

async function addCompanyByName() {
  const input = document.getElementById('company-name-input');
  const companyName = input.value.trim();

  if (!companyName) {
    alert('Please enter a company name');
    return;
  }

  const btn = event?.target || document.querySelector('.input-with-button .btn-primary');
  const btnText = document.getElementById('add-btn-text');
  const btnSpinner = document.getElementById('add-btn-spinner');

  btn.disabled = true;
  btnText.style.display = 'none';
  btnSpinner.style.display = 'inline';

  try {
    const res = await fetch(API_BASE_URL + '/api/recognize-company', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: companyName }),
    });

    const result = await res.json();

    if (result.error) {
      alert('❌ Error: ' + result.error);
      console.error('Error response:', result);
    } else {
      alert('✅ Found: ' + result.company.company_name + '\nTask ID: ' + result.task_id);
      input.value = '';

      // Show tasks section
      document.getElementById('add-company-input-section').style.display = 'none';
      document.getElementById('add-company-tasks-section').style.display = 'block';

      // Refresh tasks immediately
      await refreshTaskList();

      // Auto-refresh tasks every 2 seconds while companies view is visible
      const taskRefreshInterval = setInterval(async () => {
        const companiesView = document.querySelector('.companies-view');
        if (companiesView && companiesView.classList.contains('hidden')) {
          clearInterval(taskRefreshInterval);
        } else {
          await refreshTaskList();
        }
      }, 2000);
    }
  } catch (e) {
    alert('❌ Network Error: ' + e.message);
    console.error('Fetch error:', e);
  } finally {
    btn.disabled = false;
    btnText.style.display = 'inline';
    btnSpinner.style.display = 'none';
  }
}

async function refreshTaskList() {
  try {
    const res = await fetch(API_BASE_URL + '/api/tasks');
    const data = await res.json();
    const tasks = data.tasks || [];

    let html = '<h4>Recent Tasks</h4>';

    if (tasks.length === 0) {
      html += '<p style="color:var(--text-secondary);">No tasks yet.</p>';
    } else {
      html += '<div class="tasks-grid">';
      tasks.forEach(task => {
        const status = task.status;
        const progress = Math.round(task.progress * 100);
        const icon = status === 'completed' ? '✅' : status === 'failed' ? '❌' : status === 'running' ? '⚙️' : '⏳';

        html += `<div class="task-card status-${status}">
          <div class="task-header">
            <span>${icon} ${task.type.replace('_', ' ')}</span>
            <span class="task-time">${new Date(task.created_at).toLocaleTimeString()}</span>
          </div>
          <div class="task-companies">
            ${task.companies_added ? task.companies_added.join(', ') : 'Processing...'}
          </div>
          <div class="task-progress">
            <div class="progress-bar">
              <div class="progress-fill" style="width:${progress}%"></div>
            </div>
            <span class="progress-text">${task.current_step || 'Validating...'} (${progress}%)</span>
          </div>
          ${status === 'running' || status === 'pending' ? `
            <button class="btn-small" onclick="cancelTask('${task.id}')">Cancel</button>
          ` : ''}
          ${task.error ? `<div class="error-msg">${task.error}</div>` : ''}
        </div>`;
      });
      html += '</div>';
    }

    document.getElementById('tasks-list').innerHTML = html;
  } catch (e) {
    console.error('Error loading tasks:', e);
  }
}

async function cancelTask(taskId) {
  try {
    const res = await fetch(`/api/tasks/${taskId}/cancel`, { method: 'POST' });
    const result = await res.json();
    if (result.message) {
      alert('Task cancelled');
      refreshTaskList();
    }
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

async function searchIntelligence() {
  const query = document.getElementById('search-intelligence').value.trim();

  if (!query) {
    alert('Please enter a search query');
    return;
  }

  const btn = event?.target || document.querySelector('.btn-search-intel');
  const btnText = document.getElementById('search-btn-text');
  const btnSpinner = document.getElementById('search-btn-spinner');

  btn.disabled = true;
  btnText.style.display = 'none';
  btnSpinner.style.display = 'inline';

  try {
    // Use the AI Chat API to search across all companies
    const res = await fetch(API_BASE_URL + '/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query }),
    });

    const result = await res.json();

    if (result.error) {
      alert('Search failed: ' + result.error);
    } else {
      displaySearchResults(result, query);
    }
  } catch (e) {
    alert('Search error: ' + e.message);
  } finally {
    btn.disabled = false;
    btnText.style.display = 'inline';
    btnSpinner.style.display = 'none';
  }
}

function displaySearchResults(result, query) {
  const resultsDiv = document.getElementById('search-results');

  let html = `
    <div class="search-result-container">
      <div class="search-result-header">
        <h4>🔍 AI Analysis: "${query}"</h4>
      </div>
      <div class="search-result-content">
        <div class="ai-answer">
          ${result.answer || 'No results found'}
        </div>
  `;

  if (result.sources && result.sources.length > 0) {
    html += `<div class="search-sources">
      <h5>📚 Sources:</h5>
      <div class="source-list">`;

    result.sources.slice(0, 5).forEach(source => {
      html += `
        <div class="source-item">
          <div class="source-company">${source.company}</div>
          <div class="source-year">${source.year}</div>
          <div class="source-excerpt">${source.excerpt}</div>
          ${source.pdf_url ? `<a href="${source.pdf_url}" target="_blank" class="source-link">View PDF →</a>` : ''}
        </div>
      `;
    });

    html += `</div></div>`;
  }

  html += `</div></div>`;

  resultsDiv.innerHTML = html;
  resultsDiv.style.display = 'block';
}

// Poll for task updates every 3 seconds
setInterval(() => {
  const modal = document.getElementById('add-company-modal');
  if (!modal.classList.contains('hidden')) {
    refreshTaskList();
  }
}, 3000);

