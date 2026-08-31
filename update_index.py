import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_css = """<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

  /* ── Reset & Base ─────────────────────────────────────── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg-primary:   #09090e;
    --bg-secondary: rgba(18, 18, 26, 0.6);
    --bg-card:      rgba(22, 22, 31, 0.6);
    --bg-hover:     rgba(30, 30, 42, 0.8);
    --border:       rgba(255, 255, 255, 0.08);
    --border-focus: #818cf8;
    --text-primary: #f8fafc;
    --text-muted:   #94a3b8;
    --text-dim:     #64748b;
    --accent:       #6366f1;
    --accent-glow:  rgba(99, 102, 241, 0.4);
    --success:      #10b981;
    --success-glow: rgba(16, 185, 129, 0.4);
    --warning:      #f59e0b;
    --danger:       #ef4444;
    --gradient-1:   linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    --gradient-2:   linear-gradient(135deg, #06b6d4, #3b82f6);
    --radius:       16px;
    --radius-sm:    10px;
    --shadow:       0 8px 32px rgba(0,0,0,0.4);
    --glass-blur:   blur(12px);
  }

  body {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* ── Dynamic Mesh Background ──────────────────────────── */
  body::before, body::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    z-index: -1;
    opacity: 0.5;
    animation: float 20s ease-in-out infinite alternate;
  }

  body::before {
    top: -10%;
    left: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%);
  }

  body::after {
    bottom: -10%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 70%);
    animation-delay: -10s;
  }

  .bg-orb-3 {
    position: fixed;
    top: 40%;
    left: 60%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(236,72,153,0.1) 0%, transparent 70%);
    border-radius: 50%;
    filter: blur(80px);
    z-index: -1;
    animation: float2 25s ease-in-out infinite alternate;
  }

  @keyframes float {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(10%, 10%) scale(1.1); }
  }
  @keyframes float2 {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(-10%, -15%) scale(1.2); }
  }

  /* ── Layout ───────────────────────────────────────────── */
  .container {
    max-width: 900px;
    margin: 0 auto;
    padding: 60px 24px;
    position: relative;
    z-index: 1;
  }

  /* ── Header ───────────────────────────────────────────── */
  .header {
    text-align: center;
    margin-bottom: 56px;
    animation: fadeDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .header-icon {
    width: 72px;
    height: 72px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 24px;
    font-size: 32px;
    box-shadow: var(--shadow);
    backdrop-filter: var(--glass-blur);
    position: relative;
  }

  .header-icon::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 22px;
    background: var(--gradient-1);
    z-index: -1;
    opacity: 0.5;
    filter: blur(8px);
  }

  .header h1 {
    font-size: 40px;
    font-weight: 700;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 12px;
  }

  .header p {
    color: var(--text-muted);
    font-size: 16px;
    max-width: 500px;
    margin: 0 auto;
    font-weight: 300;
  }

  /* ── Pipeline Steps ──────────────────────────────────── */
  .pipeline {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin: 32px 0 48px;
    flex-wrap: wrap;
    position: relative;
  }

  .pipeline-step {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    border-radius: 100px;
    background: var(--bg-card);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    font-size: 14px;
    font-weight: 500;
    color: var(--text-muted);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  .pipeline-step.active {
    border-color: rgba(99, 102, 241, 0.5);
    background: rgba(99, 102, 241, 0.1);
    color: var(--text-primary);
    box-shadow: 0 0 24px var(--accent-glow);
    transform: translateY(-2px);
  }

  .pipeline-step.done {
    border-color: rgba(16, 185, 129, 0.5);
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
  }

  .pipeline-step .step-num {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    background: var(--bg-hover);
    color: var(--text-dim);
    transition: all 0.4s ease;
  }

  .pipeline-step.active .step-num {
    background: var(--accent);
    color: white;
    box-shadow: 0 0 12px var(--accent-glow);
  }

  .pipeline-step.done .step-num {
    background: var(--success);
    color: white;
  }

  .pipeline-arrow {
    color: var(--text-dim);
    font-size: 16px;
    opacity: 0.5;
  }

  /* ── Cards (Glassmorphism) ───────────────────────────── */
  .card {
    background: var(--bg-card);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 40px;
    margin-bottom: 28px;
    box-shadow: var(--shadow);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  }

  .card:hover {
    border-color: rgba(255, 255, 255, 0.15);
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  }

  .card-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-primary);
  }

  .card-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 32px;
    font-weight: 300;
  }

  /* ── Inputs & Selects ─────────────────────────────────── */
  .form-group {
    margin-bottom: 24px;
  }

  .form-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  select, input[type="text"] {
    width: 100%;
    padding: 14px 18px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 15px;
    font-family: inherit;
    transition: all 0.3s ease;
    appearance: none;
    backdrop-filter: blur(4px);
  }

  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 18px center;
  }

  select:focus, input[type="text"]:focus {
    outline: none;
    border-color: var(--accent);
    background: rgba(0, 0, 0, 0.4);
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
  }

  select:disabled, input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* ── Buttons ──────────────────────────────────────────── */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px 32px;
    border: none;
    border-radius: var(--radius-sm);
    font-size: 15px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
  }

  .btn::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(rgba(255,255,255,0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .btn:hover::after { opacity: 1; }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
  }

  .btn-primary {
    background: var(--gradient-1);
    color: white;
    box-shadow: 0 8px 24px var(--accent-glow);
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px var(--accent-glow);
  }

  .btn-success {
    background: linear-gradient(135deg, #10b981, #047857);
    color: white;
    box-shadow: 0 8px 24px var(--success-glow);
  }

  .btn-success:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px var(--success-glow);
  }

  .btn-outline {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    color: var(--text-primary);
    backdrop-filter: blur(4px);
  }

  .btn-outline:hover:not(:disabled) {
    border-color: rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.08);
    transform: translateY(-1px);
  }

  .btn-sheets {
    background: rgba(15, 157, 88, 0.1);
    border: 1px solid rgba(15, 157, 88, 0.3);
    color: #4ade80;
  }

  .btn-sheets:hover:not(:disabled) {
    background: rgba(15, 157, 88, 0.2);
    border-color: #0f9d58;
    box-shadow: 0 8px 24px rgba(15, 157, 88, 0.2);
  }

  .btn-group {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 32px;
  }

  /* ── Loading Spinner ──────────────────────────────────── */
  .spinner {
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255,255,255,0.2);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    display: inline-block;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Toast ────────────────────────────────────────────── */
  .toast-container {
    position: fixed;
    top: 32px;
    right: 32px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .toast {
    padding: 16px 24px;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 500;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 320px;
    backdrop-filter: blur(12px);
    color: white;
  }

  .toast.success {
    background: rgba(16, 185, 129, 0.8);
    border: 1px solid rgba(16, 185, 129, 0.4);
  }

  .toast.error {
    background: rgba(239, 68, 68, 0.8);
    border: 1px solid rgba(239, 68, 68, 0.4);
  }

  .toast.info {
    background: rgba(99, 102, 241, 0.8);
    border: 1px solid rgba(99, 102, 241, 0.4);
  }

  @keyframes slideIn {
    from { transform: translateX(100%) scale(0.9); opacity: 0; }
    to { transform: translateX(0) scale(1); opacity: 1; }
  }

  /* ── Summary Cards ────────────────────────────────────── */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
  }

  .stat-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease;
  }
  
  .stat-card:hover {
    transform: translateY(-4px);
    background: rgba(255,255,255,0.02);
  }

  .stat-value {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 6px;
    line-height: 1;
  }

  .stat-label {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
  }

  .stat-card.blue .stat-value { color: #60a5fa; text-shadow: 0 0 20px rgba(96,165,250,0.4); }
  .stat-card.green .stat-value { color: #34d399; text-shadow: 0 0 20px rgba(52,211,153,0.4); }
  .stat-card.yellow .stat-value { color: #fbbf24; text-shadow: 0 0 20px rgba(251,191,36,0.4); }
  .stat-card.purple .stat-value { color: #a78bfa; text-shadow: 0 0 20px rgba(167,139,250,0.4); }

  /* ── Data Table ───────────────────────────────────────── */
  .data-table-wrap {
    overflow-x: auto;
    margin-top: 20px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: rgba(0,0,0,0.2);
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }

  .data-table thead th {
    background: rgba(255,255,255,0.03);
    padding: 16px 20px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    backdrop-filter: blur(8px);
  }

  .data-table tbody td {
    padding: 14px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: var(--text-primary);
  }

  .data-table tbody tr {
    transition: background 0.2s;
  }

  .data-table tbody tr:hover {
    background: rgba(255,255,255,0.03);
  }

  .shift-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .shift-badge.s1 { background: rgba(96,165,250,0.15); color: #93c5fd; border: 1px solid rgba(96,165,250,0.3); }
  .shift-badge.s2 { background: rgba(167,139,250,0.15); color: #c4b5fd; border: 1px solid rgba(167,139,250,0.3); }
  .shift-badge.s3 { background: rgba(251,191,36,0.15); color: #fcd34d; border: 1px solid rgba(251,191,36,0.3); }
  .shift-badge.s12 { background: rgba(52,211,153,0.15); color: #6ee7b7; border: 1px solid rgba(52,211,153,0.3); }
  .shift-badge.s23 { background: rgba(251,146,60,0.15); color: #fdba74; border: 1px solid rgba(251,146,60,0.3); }
  .shift-badge.off { background: rgba(100,116,139,0.2); color: #94a3b8; border: 1px solid rgba(100,116,139,0.3); }
  .shift-badge.is { background: rgba(239,68,68,0.15); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }

  /* ── PIC Onsite Selector ──────────────────────────────── */
  .pic-onsite-selector {
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    margin-top: 16px;
  }

  .pic-radio-group {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
  }

  .pic-radio-group label {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 24px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: rgba(0,0,0,0.2);
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 15px;
    color: var(--text-primary);
  }

  .pic-radio-group label:hover {
    border-color: rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.05);
    transform: translateY(-2px);
  }

  .pic-radio-group input[type="radio"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 2px solid var(--text-muted);
    border-radius: 50%;
    outline: none;
    cursor: pointer;
    position: relative;
    transition: all 0.2s;
  }
  
  .pic-radio-group input[type="radio"]:checked {
    border-color: var(--accent);
  }

  .pic-radio-group input[type="radio"]:checked::after {
    content: '';
    position: absolute;
    inset: 4px;
    background: var(--accent);
    border-radius: 50%;
  }

  .pic-radio-group label:has(input:checked) {
    border-color: var(--accent);
    background: rgba(99, 102, 241, 0.1);
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.15);
  }

  /* ── Sections (hidden by default) ─────────────────────── */
  .section { display: none; }
  .section.visible { 
    display: block; 
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
  }

  @keyframes slideUpFade {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ── Responsive ───────────────────────────────────────── */
  @media (max-width: 640px) {
    .container { padding: 32px 16px; }
    .card { padding: 24px; }
    .header h1 { font-size: 32px; }
    .stats-grid { grid-template-columns: 1fr 1fr; }
    .pipeline { gap: 6px; }
    .pipeline-step { padding: 10px 14px; font-size: 12px; }
    .pipeline-step .step-num { width: 20px; height: 20px; font-size: 11px; }
    .pipeline-arrow { font-size: 14px; }
    .btn { width: 100%; }
  }
</style>"""

content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)
content = content.replace('<body>', '<body>\n\n<div class="bg-orb-3"></div>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
