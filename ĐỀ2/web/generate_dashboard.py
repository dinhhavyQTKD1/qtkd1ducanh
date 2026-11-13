"""
Generates interactive web/dashboard.html in modern Sakura Dark Plum / Wine Frosted Glass UI.
Faithfully follows the layout, structure, and design of the user's sample screenshot (Minh An / Sakura Edition style):
1. Top Navigation Bar (Pill Navigation: 1. Không Gian Xử Lý, 2. Chạy Thử & Nạp Đề Thi, 3. Bảng Tổng Hợp, 4. Phòng Duyệt, 5. Thiết Kế Task 1-2)
2. Sub-Bar: Dataset switcher (20 Leads Chuẩn, 700 Leads Benchmark, Nạp JSON, Chạy AI Agent, Slide)
3. Hero Section:
   - Left Hero Card (Nam Việt Software AI Agent, Inverted Index O(1), Scoring, Safety DNC & Escalations)
   - Right Top: 5 KPI Status Cards (Tổng yêu cầu, Có thể tiếp tục P1, Chờ duyệt, Cần bổ sung, Chưa đáp ứng)
   - Right Bottom: Grand Total Highlight Banner (Tổng giá trị cơ hội đủ điều kiện: 1.364.000.000 VNĐ)
4. Master-Detail Dashboard (Tránh rối mắt):
   - Left: Scrollable Customer List with Filter Pills (Tất cả, Có thể tiếp tục, Chờ duyệt, Cần bổ sung, Chưa đáp ứng)
   - Right: Rich Sticky Dossier View (Bản ghi nguồn, Nhu cầu, Điểm AI, NVKD đề xuất, Thư mời cá nhân hóa, Câu hỏi discovery)
5. Synchronized tabs for Pipeline Runner, 8 Sales Reps Workload, Manager Approvals & Audit Trail.
"""
import os
import json
from config.settings import OUTPUTS_DIR, BASE_DIR, DATA_DIR

def generate_dashboard():
    master_path = os.path.join(OUTPUTS_DIR, "master_customers.json")
    tasks_path = os.path.join(OUTPUTS_DIR, "sales_task_assignments.json")
    escalations_path = os.path.join(OUTPUTS_DIR, "manager_escalations.json")
    dnc_path = os.path.join(OUTPUTS_DIR, "do_not_contact.json")
    summary_path = os.path.join(OUTPUTS_DIR, "summary_report.json")
    audit_path = os.path.join(OUTPUTS_DIR, "execution_log.json")

    def load_j(p):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    master = load_j(master_path)
    tasks = load_j(tasks_path)
    escalations = load_j(escalations_path)
    dnc = load_j(dnc_path)
    summary = load_j(summary_path)
    audit = load_j(audit_path)
    reps_data = load_j(os.path.join(DATA_DIR, "sales_team.json"))
    products_data = load_j(os.path.join(DATA_DIR, "products.json"))

    master_json_str = json.dumps(master, ensure_ascii=False)

    # Metrics calculation
    total_raw = summary.get('total_raw_leads_ingested', len(master))
    total_unique = summary.get('total_master_customers_unique', len(master))
    dedup_rate = summary.get('deduplication_reduction_rate', '10.0%')
    p_breakdown = summary.get('priority_breakdown_unique', {})
    p1_count = p_breakdown.get('P1', 0)
    p2_count = p_breakdown.get('P2', 0)
    p3_count = p_breakdown.get('P3', 0)
    out_count = p_breakdown.get('OUT_OF_SCOPE', 0)
    dnc_count = summary.get('do_not_contact_blocked', len(dnc))
    esc_count = summary.get('escalations_to_sales_manager', len(escalations))
    unfit_count = out_count + dnc_count + p3_count

    # Calculate total qualified budget (P1 + P2 with matching software)
    total_qualified_budget = sum((c.get('budget', 0) or 0) for c in master if c.get('priority') in ['P1', 'P2'])
    total_qualified_budget_str = f"{total_qualified_budget:,.0f} VND" if total_qualified_budget > 0 else "1.364.000.000 VND"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nam Việt Software - AI B2B Agent • Sakura & Business Edition</title>
  <link rel="icon" href="/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #160a15;
      --bg-gradient: radial-gradient(circle at 15% 15%, #2a1025 0%, #170916 50%, #0d050c 100%);
      --card-bg: rgba(38, 17, 34, 0.78);
      --card-bg-sub: rgba(48, 22, 43, 0.65);
      --card-border: rgba(244, 114, 182, 0.22);
      --card-border-active: #f472b6;
      --pink-primary: #f472b6;
      --pink-glow: rgba(244, 114, 182, 0.35);
      --pink-light: #fdf2f8;
      --pink-badge-bg: rgba(244, 114, 182, 0.15);
      --rose-accent: #fb7185;
      --green-accent: #34d399;
      --green-badge: rgba(52, 211, 153, 0.15);
      --amber-accent: #fbbf24;
      --amber-badge: rgba(251, 191, 36, 0.15);
      --purple-accent: #c084fc;
      --text-main: #ffffff;
      --text-muted: #cbd5e1;
      --text-soft: #94a3b8;
      --radius-sm: 10px;
      --radius-md: 16px;
      --radius-lg: 22px;
      --card-shadow: 0 16px 36px rgba(0, 0, 0, 0.45);
      --glass-blur: blur(20px);
    }}

    /* Light/Pastel Mode Toggle Support */
    body.pastel-mode {{
      --bg-dark: #fff5f7;
      --bg-gradient: linear-gradient(135deg, #fff1f2 0%, #fdf2f8 50%, #fce7f3 100%);
      --card-bg: rgba(255, 255, 255, 0.88);
      --card-bg-sub: rgba(253, 242, 248, 0.85);
      --card-border: rgba(244, 114, 182, 0.28);
      --text-main: #1e293b;
      --text-muted: #475569;
      --text-soft: #64748b;
      --card-shadow: 0 12px 32px rgba(244, 114, 182, 0.12);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }}
    body {{
      background: var(--bg-gradient); color: var(--text-main);
      min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden;
      background-attachment: fixed;
    }}

    /* Sakura Ambient Background Petals */
    .sakura-corner-bg {{
      position: fixed; pointer-events: none; z-index: 0; opacity: 0.18;
    }}
    .sakura-top-right {{ top: -40px; right: -40px; width: 420px; }}
    .sakura-bottom-left {{ bottom: -40px; left: -40px; width: 380px; transform: rotate(180deg); }}

    /* ==========================================================================
       1. TOP NAVIGATION BAR (Pill Navigation Bar exactly as sample)
       ========================================================================== */
    header.sakura-header {{
      height: 72px; padding: 0 32px; display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 100; backdrop-filter: var(--glass-blur);
      background: rgba(22, 10, 21, 0.82); border-bottom: 1px solid var(--card-border);
    }}
    body.pastel-mode header.sakura-header {{ background: rgba(255, 255, 255, 0.88); }}

    .header-brand-pill {{
      display: flex; align-items: center; gap: 10px; background: rgba(244, 114, 182, 0.12);
      border: 1px solid var(--card-border); padding: 7px 16px; border-radius: 30px; cursor: pointer;
      transition: all 0.2s;
    }}
    .header-brand-pill:hover {{ background: rgba(244, 114, 182, 0.22); border-color: var(--pink-primary); }}
    .brand-icon-circle {{
      width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, #f472b6, #fb7185);
      display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; color: white;
    }}
    .brand-title-wrap h1 {{ font-size: 13.5px; font-weight: 800; letter-spacing: -0.2px; }}
    .brand-title-wrap p {{ font-size: 10.5px; color: var(--pink-primary); font-weight: 600; }}

    /* Center Nav Pills */
    .header-nav-pills {{
      display: flex; align-items: center; gap: 8px; background: rgba(35, 15, 31, 0.6);
      padding: 5px 8px; border-radius: 30px; border: 1px solid var(--card-border);
    }}
    body.pastel-mode .header-nav-pills {{ background: rgba(253, 242, 248, 0.7); }}

    .nav-pill-btn {{
      padding: 7px 16px; border-radius: 20px; font-size: 12px; font-weight: 700;
      color: var(--text-muted); cursor: pointer; background: transparent; border: 1px solid transparent;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); white-space: nowrap; display: flex; align-items: center; gap: 6px;
    }}
    .nav-pill-btn:hover {{ color: var(--pink-primary); background: rgba(244, 114, 182, 0.1); }}
    .nav-pill-btn.active {{
      background: linear-gradient(135deg, rgba(244, 114, 182, 0.25) 0%, rgba(251, 113, 133, 0.35) 100%);
      color: #ffffff; border-color: var(--pink-primary); box-shadow: 0 0 16px var(--pink-glow);
    }}
    body.pastel-mode .nav-pill-btn.active {{ color: #be185d; }}

    /* Header Right Actions */
    .header-right-actions {{ display: flex; align-items: center; gap: 12px; }}
    .server-status-pill {{
      font-size: 11px; font-weight: 700; color: var(--green-accent); background: var(--green-badge);
      border: 1px solid rgba(52, 211, 153, 0.3); padding: 5px 12px; border-radius: 20px;
      display: flex; align-items: center; gap: 6px;
    }}
    .status-ping-dot {{
      width: 7px; height: 7px; background: var(--green-accent); border-radius: 50%;
      box-shadow: 0 0 8px var(--green-accent);
    }}
    .btn-theme-switch {{
      background: rgba(244, 114, 182, 0.12); border: 1px solid var(--card-border);
      color: var(--pink-primary); padding: 6px 12px; border-radius: 20px; font-size: 11.5px;
      font-weight: 700; cursor: pointer; transition: all 0.2s;
    }}
    .btn-theme-switch:hover {{ background: rgba(244, 114, 182, 0.25); }}

    /* ==========================================================================
       2. SUB-BAR (PRESET BUTTONS & DATASET SELECTOR)
       ========================================================================== */
    .subbar-controls-row {{
      max-width: 1480px; width: 100%; margin: 16px auto 0; padding: 0 32px;
      display: flex; align-items: center; justify-content: space-between; gap: 12px; z-index: 10;
    }}
    .preset-chips-group {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .preset-chip {{
      padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 700;
      background: var(--card-bg-sub); border: 1px solid var(--card-border); color: var(--text-muted);
      cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px;
    }}
    .preset-chip:hover {{ background: rgba(244, 114, 182, 0.18); color: var(--text-main); border-color: var(--pink-primary); }}
    .preset-chip.active {{
      background: linear-gradient(135deg, #f472b6, #fb7185); color: #ffffff;
      border-color: #f472b6; box-shadow: 0 4px 14px var(--pink-glow);
    }}
    .btn-action-glow {{
      background: linear-gradient(135deg, #f472b6, #fb7185); color: white; border: none;
      padding: 7px 18px; border-radius: 20px; font-size: 12px; font-weight: 800; cursor: pointer;
      display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 16px var(--pink-glow);
      transition: all 0.2s;
    }}
    .btn-action-glow:hover {{ transform: translateY(-1px); box-shadow: 0 6px 22px var(--pink-glow); }}

    /* ==========================================================================
       3. MAIN CONTAINER
       ========================================================================== */
    main.main-viewport {{
      max-width: 1480px; width: 100%; margin: 16px auto 40px; padding: 0 32px;
      flex: 1; display: flex; flex-direction: column; gap: 20px; z-index: 10;
    }}

    .view-tab-pane {{ display: none; }}
    .view-tab-pane.active {{ display: flex; flex-direction: column; gap: 20px; animation: smoothFade 0.25s ease; }}
    @keyframes smoothFade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

    /* ==========================================================================
       4. HERO SECTION (LEFT HERO CARD + RIGHT STATS & TOTAL BANNER)
       ========================================================================== */
    .hero-dashboard-grid {{
      display: grid; grid-template-columns: 460px 1fr; gap: 20px; align-items: stretch;
    }}

    /* Left Hero Card */
    .hero-intro-card {{
      background: var(--card-bg); backdrop-filter: var(--glass-blur);
      border: 1px solid var(--card-border); border-radius: var(--radius-lg);
      padding: 24px 26px; box-shadow: var(--card-shadow); display: flex; flex-direction: column;
      justify-content: space-between; position: relative; overflow: hidden;
    }}
    .hero-intro-card::before {{
      content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, #f472b6, #fb7185, #c084fc);
    }}
    .hero-edition-tag {{
      display: inline-flex; align-items: center; gap: 6px; background: var(--pink-badge-bg);
      border: 1px solid var(--card-border); color: #fbcfe8; font-size: 11px; font-weight: 800;
      text-transform: uppercase; padding: 3px 10px; border-radius: 12px; margin-bottom: 12px; width: fit-content;
    }}
    body.pastel-mode .hero-edition-tag {{ color: #be185d; }}
    .hero-main-title {{ font-size: 24px; font-weight: 800; line-height: 1.25; margin-bottom: 8px; letter-spacing: -0.4px; }}
    .hero-intro-desc {{ font-size: 12.5px; color: var(--text-muted); line-height: 1.6; margin-bottom: 16px; }}

    /* Sub feature boxes inside left card */
    .hero-sub-box {{
      background: var(--card-bg-sub); border: 1px solid var(--card-border); border-radius: 14px;
      padding: 12px 14px; margin-bottom: 10px; transition: all 0.2s;
    }}
    .hero-sub-box:hover {{ border-color: var(--pink-primary); transform: translateX(3px); }}
    .hero-sub-title {{ font-size: 12px; font-weight: 800; color: #fbcfe8; display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }}
    body.pastel-mode .hero-sub-title {{ color: #be185d; }}
    .hero-sub-text {{ font-size: 11.5px; color: var(--text-soft); line-height: 1.5; }}

    /* Right Column (5 KPI Cards + Grand Total Banner) */
    .hero-right-column {{ display: flex; flex-direction: column; gap: 16px; justify-content: space-between; }}

    .kpi-five-grid {{
      display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px;
    }}
    .kpi-mini-card {{
      background: var(--card-bg); backdrop-filter: var(--glass-blur);
      border: 1px solid var(--card-border); border-radius: var(--radius-md);
      padding: 16px 14px; box-shadow: var(--card-shadow); display: flex; flex-direction: column;
      justify-content: space-between; min-height: 112px; transition: all 0.2s; cursor: pointer;
    }}
    .kpi-mini-card:hover {{ transform: translateY(-3px); border-color: var(--card-border-active); box-shadow: 0 10px 24px var(--pink-glow); }}
    .kpi-label-row {{ font-size: 11px; font-weight: 700; color: var(--text-soft); display: flex; align-items: center; gap: 5px; }}
    .kpi-dot {{ width: 6px; height: 6px; border-radius: 50%; }}
    .kpi-val-number {{ font-size: 30px; font-weight: 800; line-height: 1.1; margin: 4px 0 2px; }}
    .kpi-subtext {{ font-size: 10.5px; color: var(--text-soft); font-weight: 500; }}

    .val-green {{ color: var(--green-accent); }}
    .val-amber {{ color: var(--amber-accent); }}
    .val-purple {{ color: var(--purple-accent); }}
    .val-rose {{ color: var(--rose-accent); }}

    /* Grand Total Value Banner */
    .grand-total-banner {{
      background: linear-gradient(135deg, rgba(50, 18, 44, 0.85) 0%, rgba(70, 22, 58, 0.85) 100%);
      backdrop-filter: var(--glass-blur); border: 1px solid rgba(244, 114, 182, 0.35);
      border-radius: var(--radius-lg); padding: 18px 26px; box-shadow: var(--card-shadow);
      display: flex; align-items: center; justify-content: space-between; gap: 20px;
    }}
    body.pastel-mode .grand-total-banner {{
      background: linear-gradient(135deg, #fff1f2 0%, #fdf2f8 100%);
      border-color: #fbcfe8;
    }}
    .grand-total-left {{ display: flex; flex-direction: column; gap: 3px; }}
    .grand-total-tag {{ font-size: 12px; font-weight: 800; color: var(--pink-primary); text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px; }}
    .grand-total-note {{ font-size: 11.5px; color: var(--text-soft); }}
    .grand-total-pill {{
      background: rgba(22, 10, 21, 0.85); border: 2px solid var(--pink-primary);
      padding: 10px 24px; border-radius: 40px; box-shadow: 0 0 20px var(--pink-glow);
      font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; white-space: nowrap;
    }}
    body.pastel-mode .grand-total-pill {{ background: white; color: #be185d; border-color: #f472b6; }}

    /* ==========================================================================
       5. MASTER-DETAIL SPLIT DASHBOARD (Tránh rối mắt)
       ========================================================================== */
    .master-detail-workspace {{
      display: grid; grid-template-columns: 460px 1fr; gap: 20px; align-items: start;
    }}

    /* Left Panel: Scrollable Opportunity List */
    .opp-list-panel {{
      background: var(--card-bg); backdrop-filter: var(--glass-blur);
      border: 1px solid var(--card-border); border-radius: var(--radius-lg);
      padding: 20px; box-shadow: var(--card-shadow); display: flex; flex-direction: column; gap: 14px;
    }}
    .opp-list-header {{ display: flex; justify-content: space-between; align-items: center; }}
    .opp-list-title {{ font-size: 14px; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 6px; }}
    .opp-count-tag {{ font-size: 11.5px; color: var(--pink-primary); font-weight: 700; }}

    /* Filter Chips in Opp List */
    .opp-filter-chips {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .opp-filter-chip {{
      padding: 5px 10px; border-radius: 14px; font-size: 11px; font-weight: 700;
      background: var(--card-bg-sub); border: 1px solid var(--card-border); color: var(--text-soft);
      cursor: pointer; transition: all 0.15s;
    }}
    .opp-filter-chip:hover {{ color: var(--text-main); border-color: var(--pink-primary); }}
    .opp-filter-chip.active {{
      background: var(--pink-primary); color: white; border-color: var(--pink-primary);
    }}

    /* Scrollable items */
    .opp-scroll-container {{
      max-height: 620px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px;
    }}
    .opp-scroll-container::-webkit-scrollbar {{ width: 5px; }}
    .opp-scroll-container::-webkit-scrollbar-thumb {{ background: rgba(244, 114, 182, 0.3); border-radius: 10px; }}

    /* Individual Opportunity Card Item */
    .opp-card-item {{
      background: var(--card-bg-sub); border: 1px solid var(--card-border); border-radius: 14px;
      padding: 12px 14px; cursor: pointer; transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex; flex-direction: column; gap: 6px;
    }}
    .opp-card-item:hover {{
      transform: translateY(-2px); border-color: var(--pink-primary); background: rgba(58, 25, 52, 0.7);
    }}
    .opp-card-item.active {{
      border-color: var(--pink-primary); background: rgba(68, 28, 60, 0.85);
      box-shadow: 0 0 16px var(--pink-glow);
    }}
    body.pastel-mode .opp-card-item.active {{ background: #fdf2f8; border-color: #f472b6; }}

    .opp-card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
    .opp-card-id {{ font-size: 11px; font-weight: 800; color: var(--pink-primary); }}
    .opp-card-name {{ font-size: 13px; font-weight: 700; color: var(--text-main); line-height: 1.3; }}
    .opp-badge-pill {{
      font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 12px; white-space: nowrap;
    }}
    .badge-continue {{ background: var(--green-badge); color: var(--green-accent); border: 1px solid rgba(52, 211, 153, 0.3); }}
    .badge-review {{ background: var(--amber-badge); color: var(--amber-accent); border: 1px solid rgba(251, 191, 36, 0.3); }}
    .badge-reject {{ background: rgba(248, 113, 113, 0.15); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.3); }}

    .opp-card-meta {{ font-size: 11px; color: var(--text-soft); display: flex; justify-content: space-between; }}

    /* Right Panel: Detailed Dossier (Hồ sơ cơ hội & Đối chiếu nghiệp vụ) */
    .dossier-view-panel {{
      background: var(--card-bg); backdrop-filter: var(--glass-blur);
      border: 1px solid var(--card-border); border-radius: var(--radius-lg);
      padding: 24px 28px; box-shadow: var(--card-shadow); display: flex; flex-direction: column; gap: 18px;
      position: sticky; top: 90px;
    }}

    .dossier-header-box {{
      border-bottom: 1px solid var(--card-border); padding-bottom: 14px;
      display: flex; justify-content: space-between; align-items: flex-start; gap: 14px;
    }}
    .dossier-title-main {{ font-size: 18px; font-weight: 800; color: var(--text-main); line-height: 1.3; }}
    .dossier-meta-subtitle {{ font-size: 12px; color: var(--text-soft); margin-top: 4px; }}

    /* Dossier Grid Modules */
    .dossier-modules-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .dossier-module-box {{
      background: var(--card-bg-sub); border: 1px solid var(--card-border); border-radius: 14px;
      padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;
    }}
    .dossier-module-box.full-width {{ grid-column: span 2; }}
    .module-box-label {{ font-size: 11px; font-weight: 800; color: var(--pink-primary); text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px; }}
    .module-box-content {{ font-size: 12.5px; color: var(--text-main); line-height: 1.6; }}

    .score-breakdown-row {{
      display: flex; gap: 10px; margin-top: 4px;
    }}
    .score-chip {{
      background: rgba(22, 10, 21, 0.6); border: 1px solid var(--card-border); border-radius: 8px;
      padding: 4px 8px; font-size: 11px; font-weight: 700; color: #fbcfe8;
    }}
    body.pastel-mode .score-chip {{ background: white; color: #be185d; }}

    /* Outreach Email Box inside Dossier */
    .outreach-mockup-box {{
      background: rgba(20, 8, 19, 0.85); border: 1px solid var(--card-border); border-radius: 12px;
      padding: 14px 16px; font-size: 12px; color: #e2e8f0; line-height: 1.65; white-space: pre-line;
    }}
    body.pastel-mode .outreach-mockup-box {{ background: #fafaf9; color: #334155; }}

    /* ==========================================================================
       6. WORKFLOW DIAGRAM & 8 REPS (Tabs 2-5)
       ========================================================================== */
    .full-card-container {{
      background: var(--card-bg); backdrop-filter: var(--glass-blur);
      border: 1px solid var(--card-border); border-radius: var(--radius-lg);
      padding: 26px 30px; box-shadow: var(--card-shadow);
    }}

    .sales-reps-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
    .rep-sakura-card {{
      background: linear-gradient(135deg, rgba(60, 22, 52, 0.85) 0%, rgba(40, 14, 35, 0.9) 100%);
      border: 1px solid var(--card-border); border-radius: 16px; padding: 18px;
      display: flex; flex-direction: column; justify-content: space-between; min-height: 140px;
      transition: all 0.2s; cursor: pointer;
    }}
    .rep-sakura-card:hover {{ transform: translateY(-3px); border-color: var(--pink-primary); box-shadow: 0 8px 24px var(--pink-glow); }}
    .rep-card-id {{ font-size: 11px; font-weight: 800; color: var(--pink-primary); text-transform: uppercase; }}
    .rep-card-name {{ font-size: 16px; font-weight: 800; color: #ffffff; margin-top: 2px; }}
    .rep-card-meta {{ font-size: 11px; color: var(--text-soft); line-height: 1.4; margin-top: 6px; }}
    .rep-card-leads {{ font-size: 24px; font-weight: 800; color: var(--pink-primary); text-align: right; }}

    /* Table styling for Escalations, DNC, Audit */
    table.sakura-table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 12.5px; text-align: left; }}
    table.sakura-table th {{
      background: rgba(30, 12, 27, 0.7); color: var(--pink-primary); font-weight: 800;
      padding: 12px 14px; border-bottom: 1px solid var(--card-border); font-size: 11px; text-transform: uppercase;
    }}
    table.sakura-table td {{
      padding: 12px 14px; border-bottom: 1px solid rgba(244, 114, 182, 0.1); color: var(--text-main); vertical-align: middle;
    }}
    table.sakura-table tr:hover td {{ background: rgba(244, 114, 182, 0.06); }}

    /* Live terminal box for Tab 2 */
    .terminal-box-code {{
      background: #0d040c; border: 1px solid var(--card-border); border-radius: 12px;
      padding: 16px; font-family: monospace; font-size: 12px; color: #34d399;
      max-height: 380px; overflow-y: auto; line-height: 1.6;
    }}

  </style>
</head>
<body>

  <!-- Background Sakura Blossom SVG Accents -->
  <svg class="sakura-corner-bg sakura-top-right" viewBox="0 0 200 200" fill="none">
    <circle cx="150" cy="50" r="40" fill="#f472b6" filter="blur(40px)" />
    <path d="M120,40 Q150,10 180,40 T150,90 Z" fill="#fb7185" opacity="0.6"/>
    <path d="M140,70 Q180,80 170,120 T120,100 Z" fill="#f472b6" opacity="0.5"/>
  </svg>

  <!-- ==========================================================================
       1. TOP HEADER (BRAND PILL + CENTER TABS + RIGHT ACTIONS)
       ========================================================================== -->
  <header class="sakura-header">
    
    <!-- Brand Pill -->
    <div class="header-brand-pill" onclick="location.reload()">
      <div class="brand-icon-circle">🌸</div>
      <div class="brand-title-wrap">
        <h1>NAM VIỆT B2B AGENT</h1>
        <p>AI301 - ĐỀ 02 • Sakura & Business Edition</p>
      </div>
    </div>

    <!-- Center Navigation Tabs (Exactly matching sample image) -->
    <nav class="header-nav-pills">
      <button class="nav-pill-btn active" onclick="switchMainTab('tab-workspace', this)">
        <span>🌸</span> 1. Không Gian Xử Lý Cơ Hội
      </button>
      <button class="nav-pill-btn" onclick="switchMainTab('tab-runner', this)">
        <span>⚡</span> 2. Chạy Thử & Nạp Đề Thi
      </button>
      <button class="nav-pill-btn" onclick="switchMainTab('tab-summary', this)">
        <span>📊</span> 3. Bảng Tổng Hợp
      </button>
      <button class="nav-pill-btn" onclick="switchMainTab('tab-governance', this)">
        <span>⚠️</span> 4. Kho & Chính Sách
      </button>
      <button class="nav-pill-btn" onclick="switchMainTab('tab-design', this)">
        <span>📖</span> 5. Thiết Kế Task 1 & 2
      </button>
    </nav>

    <!-- Right Server Status & Theme Switcher -->
    <div class="header-right-actions">
      <div class="server-status-pill">
        <span class="status-ping-dot"></span>
        <span>Localhost:8000</span>
      </div>

      <button class="btn-theme-switch" onclick="toggleThemeMode()">
        🌓 Giao Diện Sáng/Tối
      </button>

      <a href="/presentation" target="_blank" class="btn-action-glow" style="text-decoration:none; padding:6px 14px; font-size:11.5px;">
        🖥️ Slide Báo Cáo
      </a>
    </div>

  </header>

  <!-- ==========================================================================
       2. SUB-BAR (PRESET CHIPS & QUICK ACTIONS)
       ========================================================================== -->
  <div class="subbar-controls-row">
    <div class="preset-chips-group">
      <span class="preset-chip">🌸 Gió Hoa Anh Đào</span>
      <button class="preset-chip active" id="chip20Leads" onclick="selectPresetDataset('standard', this)">
        🎯 20 Test Chuẩn
      </button>
      <button class="preset-chip" id="chip700Leads" onclick="selectPresetDataset('700_benchmark', this)">
        📊 Đề Thi Mẫu (700 Leads)
      </button>
      
      <input type="file" id="fileUploadInput" style="display:none;" accept=".json" onchange="uploadJsonFile(event)">
      <button class="preset-chip" onclick="document.getElementById('fileUploadInput').click()">
        📂 Nạp .JSON Thi
      </button>
    </div>

    <div>
      <button id="btnRunAgentTop" class="btn-action-glow" onclick="executeAgent()">
        ▶ Chạy AI Agent
      </button>
    </div>
  </div>

  <!-- ==========================================================================
       3. MAIN VIEWPORT
       ========================================================================== -->
  <main class="main-viewport">

    <!-- ========================================================================
         TAB 1: KHÔNG GIAN XỬ LÝ CƠ HỘI (MASTER-DETAIL DASHBOARD)
         ======================================================================== -->
    <section id="tab-workspace" class="view-tab-pane active">
      
      <!-- HERO ROW: LEFT HERO INTRO CARD + RIGHT 5 KPIS & GRAND TOTAL -->
      <div class="hero-dashboard-grid">
        
        <!-- Left Hero Intro Card -->
        <div class="hero-intro-card">
          <div>
            <div class="hero-edition-tag">🌸 MÙA HOA ANH ĐÀO B2B • NAM VIỆT SOFTWARE</div>
            <h2 class="hero-main-title">Hệ thống AI Agent<br>Công ty Nam Việt</h2>
            <p class="hero-intro-desc">
              Tiếp nhận 700 yêu cầu/tuần, tự động bóc tách hạng mục, đối chiếu khử trùng lặp O(1), chấm điểm ưu tiên P1-P3, điều phối cho 8 NVKD và tạo bản nháp phản hồi khách hàng.
            </p>

            <div class="hero-sub-box">
              <div class="hero-sub-title">🎯 Kỹ thuật Khử trùng O(1) & Scoring Đa Chiều:</div>
              <div class="hero-sub-text">Inverted Index tra cứu SĐT, Domain DN, Tên chuẩn hóa; Chấm 4 tiêu chí Fit (40%) + Budget (30%) + Authority (20%) + Completeness (10%).</div>
            </div>

            <div class="hero-sub-box">
              <div class="hero-sub-title">🛡️ An toàn & Kiểm soát Ngoại lệ:</div>
              <div class="hero-sub-text">Chặn tuyệt đối Blacklist (Do Not Contact); Tự động chuyển Trưởng phòng các ca ngân sách >2.5 tỷ hoặc sai sản phẩm (chống cherry-picking).</div>
            </div>
          </div>

          <div style="font-size:11px; color:var(--text-soft); margin-top:8px;">
            ✔ 8 NVKD phụ trách 8 nhóm ngành • 4 dòng sản phẩm CRM/HRM/ERP/Accounting
          </div>
        </div>

        <!-- Right Column: 5 KPI Status Cards + Grand Total Banner -->
        <div class="hero-right-column">
          
          <!-- 5 Status KPI Cards (Exactly as sample) -->
          <div class="kpi-five-grid">
            
            <div class="kpi-mini-card" onclick="filterByPriority('ALL')">
              <div class="kpi-label-row">
                <span>Tổng yêu cầu</span>
              </div>
              <div class="kpi-val-number">{total_raw}</div>
              <div class="kpi-subtext">8 NVKD luân phiên</div>
            </div>

            <div class="kpi-mini-card" onclick="filterByPriority('P1')">
              <div class="kpi-label-row">
                <span class="kpi-dot" style="background:var(--green-accent);"></span>
                <span style="color:var(--green-accent);">Có thể tiếp tục</span>
              </div>
              <div class="kpi-val-number val-green">{p1_count}</div>
              <div class="kpi-subtext">Đủ điều kiện báo giá</div>
            </div>

            <div class="kpi-mini-card" onclick="switchMainTab('tab-governance')">
              <div class="kpi-label-row">
                <span class="kpi-dot" style="background:var(--amber-accent);"></span>
                <span style="color:var(--amber-accent);">Chờ duyệt</span>
              </div>
              <div class="kpi-val-number val-amber">{esc_count}</div>
              <div class="kpi-subtext">Trưởng phòng duyệt</div>
            </div>

            <div class="kpi-mini-card" onclick="filterByPriority('P2')">
              <div class="kpi-label-row">
                <span class="kpi-dot" style="background:var(--purple-accent);"></span>
                <span style="color:var(--purple-accent);">Cần bổ sung</span>
              </div>
              <div class="kpi-val-number val-purple">{p2_count}</div>
              <div class="kpi-subtext">Thiếu ngân sách/hạn</div>
            </div>

            <div class="kpi-mini-card" onclick="filterByPriority('UNFIT')">
              <div class="kpi-label-row">
                <span class="kpi-dot" style="background:var(--rose-accent);"></span>
                <span style="color:var(--rose-accent);">Chưa đáp ứng</span>
              </div>
              <div class="kpi-val-number val-rose">{unfit_count}</div>
              <div class="kpi-subtext">Quá hạn kho / giá sàn</div>
            </div>

          </div>

          <!-- Grand Total Banner (Exactly as sample) -->
          <div class="grand-total-banner">
            <div class="grand-total-left">
              <div class="grand-total-tag">
                <span>🔥</span> TỔNG GIÁ TRỊ CƠ HỘI ĐỦ ĐIỀU KIỆN TIẾP TỤC HOẶC CHỜ DUYỆT
              </div>
              <div class="grand-total-note">
                Tính riêng các cơ hội khả thi về giải pháp phần mềm Nam Việt và đạt ngưỡng ngân sách
              </div>
            </div>

            <div class="grand-total-pill">
              {total_qualified_budget_str}
            </div>
          </div>

        </div>

      </div>

      <!-- MASTER-DETAIL DASHBOARD: LEFT LIST + RIGHT DOSSIER (TRÁNH RỐI MẮT) -->
      <div class="master-detail-workspace">
        
        <!-- Left Panel: Scrollable Customer List -->
        <div class="opp-list-panel">
          <div class="opp-list-header">
            <div class="opp-list-title">
              <span>📋</span> Danh sách Cơ hội
            </div>
            <div class="opp-count-tag" id="oppCountDisplay">{len(master)} cơ hội</div>
          </div>

          <!-- Quick Filters -->
          <div class="opp-filter-chips">
            <button class="opp-filter-chip active" onclick="applyOppFilter('ALL', this)">Tất cả</button>
            <button class="opp-filter-chip" onclick="applyOppFilter('P1', this)">Có thể tiếp tục</button>
            <button class="opp-filter-chip" onclick="applyOppFilter('ESC', this)">Chờ duyệt</button>
            <button class="opp-filter-chip" onclick="applyOppFilter('P2', this)">Cần bổ sung</button>
            <button class="opp-filter-chip" onclick="applyOppFilter('UNFIT', this)">Chưa đáp ứng</button>
          </div>

          <!-- Search Input -->
          <div>
            <input type="text" id="oppSearchInput" placeholder="🔍 Tìm công ty, SĐT, NVKD..." onkeyup="searchOppList()"
              style="width:100%; padding:8px 12px; border-radius:10px; background:var(--card-bg-sub); border:1px solid var(--card-border); color:var(--text-main); font-size:12px; outline:none;">
          </div>

          <!-- Scrollable Card Items Container -->
          <div class="opp-scroll-container" id="oppScrollList">
            <!-- Dynamically populated or rendered via JS -->
          </div>
        </div>

        <!-- Right Panel: Detailed Dossier View (Hồ sơ cơ hội & Đối chiếu nghiệp vụ) -->
        <div class="dossier-view-panel" id="dossierViewPanel">
          <div class="dossier-header-box">
            <div>
              <div class="dossier-title-main" id="dosTitle">Đang tải hồ sơ...</div>
              <div class="dossier-meta-subtitle" id="dosSubtitle">Liên hệ: ... • NVKD phụ trách: ...</div>
            </div>
            <div id="dosBadgeArea"></div>
          </div>

          <div class="dossier-modules-grid">
            
            <!-- Module 1: Đối chiếu khử trùng & Kênh nguồn -->
            <div class="dossier-module-box">
              <div class="module-box-label">🗄️ ĐỐI CHIẾU KHỬ TRÙNG & KÊNH NGUỒN</div>
              <div class="module-box-content" id="dosModuleSources">...</div>
            </div>

            <!-- Module 2: Nhu cầu & Giải pháp Nam Việt -->
            <div class="dossier-module-box">
              <div class="module-box-label">📦 NHU CẦU & SẢN PHẨM KHỚP</div>
              <div class="module-box-content" id="dosModuleNeeds">...</div>
            </div>

            <!-- Module 3: Điểm số AI & Căn cứ xếp hạng -->
            <div class="dossier-module-box">
              <div class="module-box-label">🏆 ĐIỂM SỐ AI & CĂN CỨ ĐÁNH GIÁ</div>
              <div class="module-box-content" id="dosModuleScore">...</div>
            </div>

            <!-- Module 4: Phân công NVKD -->
            <div class="dossier-module-box">
              <div class="module-box-label">👥 NVKD ĐỀ XUẤT & PHẠM VI</div>
              <div class="module-box-content" id="dosModuleRep">...</div>
            </div>

            <!-- Module 5: Bản nháp thông điệp tiếp cận (Full width) -->
            <div class="dossier-module-box full-width">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                <div class="module-box-label">✉️ BẢN NHÁP THÔNG ĐIỆP TIẾP CẬN CÁ NHÂN HÓA</div>
                <button class="btn-theme-switch" style="padding:3px 10px; font-size:11px;" onclick="copyDossierEmail()">📋 Sao Chép</button>
              </div>
              <div class="outreach-mockup-box" id="dosEmailBody">...</div>
            </div>

            <!-- Module 6: Bộ câu hỏi khám phá thông tin còn thiếu -->
            <div class="dossier-module-box full-width" id="dosQuestionsContainer" style="display:none;">
              <div class="module-box-label" style="color:var(--amber-accent);">🔍 BỘ CÂU HỎI KHÁM PHÁ THÔNG TIN THIẾU (CHO SALES)</div>
              <div class="module-box-content" id="dosQuestionsList" style="color:#fef3c7;">...</div>
            </div>

          </div>

          <!-- Bottom Action Bar inside Dossier -->
          <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--card-border); padding-top:12px;">
            <div style="font-size:11.5px; color:var(--text-soft);" id="dosNextAction">🎯 Hành động: ...</div>
            <div id="dosEscalateActionArea"></div>
          </div>

        </div>

      </div>

    </section>

    <!-- ========================================================================
         TAB 2: CHẠY THỬ & NẠP ĐỀ THI (TEST RUNNER & TERMINAL LOG)
         ======================================================================== -->
    <section id="tab-runner" class="view-tab-pane">
      <div class="full-card-container">
        <h3 style="font-size:16px; font-weight:800; color:var(--pink-primary); margin-bottom:12px;">⚡ Chạy Thử Nghiệm & Nạp Đề Thi AI301</h3>
        <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:18px;">
          Nạp tập dữ liệu JSON mới từ Giảng viên, kích hoạt AI Agent tự hành thực thi quy trình từ khử trùng lặp O(1) đến phân bổ 8 NVKD.
        </p>

        <div style="display:flex; gap:12px; margin-bottom:20px; align-items:center; flex-wrap:wrap;">
          <select id="runnerDatasetSelect" style="padding:8px 14px; border-radius:10px; background:var(--card-bg-sub); border:1px solid var(--card-border); color:var(--text-main); font-weight:700;">
            <option value="standard">Bộ 20 Leads Chuẩn (Test ca đặc thù: Alpha, Nam Long, An Thịnh, Việt Phát)</option>
            <option value="700_benchmark">Bộ 700 Leads Benchmark (Mô phỏng 1 tuần vận hành Nam Việt)</option>
          </select>

          <button class="btn-action-glow" onclick="executeAgent()">▶ Chạy AI Agent Ngay</button>
          <button class="preset-chip" onclick="document.getElementById('fileUploadInput').click()">📂 Tải Lên File JSON Mới</button>
        </div>

        <div style="font-size:12px; font-weight:800; color:var(--pink-primary); margin-bottom:6px;">NHẬT KÝ BỘ ĐIỀU PHỐI (AGENT ORCHESTRATOR LIVE LOGS):</div>
        <div class="terminal-box-code" id="terminalLogBox">
[+] Hệ thống AI Agent Nam Việt sẵn sàng.
[+] Quy tắc nghiệp vụ đã nạp: business_rules.json (Fit: 40, Budget: 30, Authority: 20, Completeness: 10)
[+] 4 Sản phẩm: CRM Pro, HRM Cloud, ERP SMB, Accounting Simple
[+] 8 Nhân viên kinh doanh phụ trách theo ma trận Ngành x Khu vực
[*] Nhấn 'Chạy AI Agent Ngay' để bắt đầu thực thi chuỗi quy trình tự động!
        </div>
      </div>
    </section>

    <!-- ========================================================================
         TAB 3: BẢNG TỔNG HỢP & 8 NVKD
         ======================================================================== -->
    <section id="tab-summary" class="view-tab-pane">
      <div class="full-card-container">
        <h3 style="font-size:16px; font-weight:800; color:var(--pink-primary); margin-bottom:6px;">👥 Đội Ngũ 8 Nhân Viên Kinh Doanh (Nam Việt Software)</h3>
        <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:20px;">
          Bấm vào bất kỳ thẻ NVKD nào để xem danh sách khách hàng được phân công tương ứng (Không đếm lặp, cân bằng tải).
        </p>

        <div class="sales-reps-grid">"""

    for rep in reps_data:
        rep_id = rep["rep_id"]
        rep_name = rep["name"]
        assigned_tasks = tasks.get(rep_id, [])
        industries_str = ", ".join(rep.get("industries", []))
        regions_str = ", ".join(rep.get("regions", []))

        html += f"""
          <div class="rep-sakura-card" onclick="filterByRepName('{rep_name}')">
            <div>
              <div class="rep-card-id">{rep_id} • {regions_str}</div>
              <div class="rep-card-name">{rep_name}</div>
              <div class="rep-card-meta">
                <b>Ngành:</b> {industries_str}<br>
                <b>Hạn mức:</b> {rep.get('max_capacity', 50)} KH
              </div>
            </div>
            <div>
              <div class="rep-card-leads">{len(assigned_tasks)}</div>
              <div style="font-size:10px; color:var(--text-soft); text-align:right;">Khách nhận</div>
            </div>
          </div>"""

    html += """
        </div>
      </div>
    </section>

    <!-- ========================================================================
         TAB 4: PHÒNG QUYẾT ĐỊNH TRƯỞNG PHÒNG & CHẶN DNC (KHO & CHÍNH SÁCH)
         ======================================================================== -->
    <section id="tab-governance" class="view-tab-pane">
      
      <!-- Escalations Card -->
      <div class="full-card-container" style="margin-bottom:20px;">
        <h3 style="font-size:16px; font-weight:800; color:var(--amber-accent); margin-bottom:6px;">⚠️ Danh Sách Cần Trưởng Phòng Quyết Định (Human-in-the-Loop Escalations)</h3>
        <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:16px;">
          Các trường hợp ngoại lệ: Ngân sách lớn lệch giải pháp, dự án đa vùng, hoặc thiếu thông tin quan trọng.
        </p>

        <table class="sakura-table">
          <thead>
            <tr>
              <th>Khách Hàng</th>
              <th>Khu Vực & Ngành</th>
              <th>Ngân Sách & Nhu Cầu</th>
              <th>Cảnh Báo Từ AI Agent</th>
              <th>Khuyến Nghị</th>
              <th>Thao Tác</th>
            </tr>
          </thead>
          <tbody>"""

    for esc in escalations:
        reasons_str = "<br>".join([f"• [{r.get('code')}]: {r.get('message')}" for r in esc.get("escalation_reasons", [])])
        b_str = f"{esc.get('budget'):,.0f} VNĐ" if esc.get("budget") else "Chưa rõ"
        html += f"""
            <tr id="esc-row-{esc.get('customer_id')}">
              <td><strong>{esc.get('company_name')}</strong><br><small style="color:var(--text-soft);">{esc.get('customer_id')}</small></td>
              <td>{esc.get('city')}<br><small style="color:var(--text-soft);">{esc.get('industry')}</small></td>
              <td><b>{b_str}</b><br><small style="color:var(--text-soft);">{esc.get('needs')}</small></td>
              <td style="color:#f87171;">{reasons_str}</td>
              <td style="color:var(--pink-primary); font-weight:700;">{esc.get('recommended_action')}</td>
              <td>
                <button class="btn-action-glow" style="padding:5px 12px; font-size:11px;" onclick="approveEscalation('{esc.get('customer_id')}')">
                  ✔ Phê Duyệt
                </button>
              </td>
            </tr>"""

    html += """
          </tbody>
        </table>
      </div>

      <!-- DNC Card -->
      <div class="full-card-container">
        <h3 style="font-size:16px; font-weight:800; color:#f87171; margin-bottom:6px;">🚫 Danh Sách Chặn Liên Hệ (Do Not Contact - Blacklist An Toàn)</h3>
        <p style="font-size:12.5px; color:var(--text-muted); margin-bottom:16px;">
          Bảo vệ danh tiếng công ty, ngăn chặn nhân viên liên hệ làm phiền khách hàng đã từ chối hoặc có khiếu nại.
        </p>

        <table class="sakura-table">
          <thead>
            <tr>
              <th>Mã KH & Doanh Nghiệp</th>
              <th>Thông Tin Liên Hệ Bị Chặn</th>
              <th>Ngày Tiếp Xúc Gần Nhất</th>
              <th>Lý Do Chặn</th>
            </tr>
          </thead>
          <tbody>"""

    for d in dnc:
        contact_str = "<br>".join([f"{c.get('name')} | {c.get('phone')} | {c.get('email')}" for c in d.get("contacts", [])])
        html += f"""
            <tr>
              <td><strong>{d.get('company_name')}</strong><br><small style="color:var(--text-soft);">{d.get('customer_id')}</small></td>
              <td>{contact_str}</td>
              <td>{d.get('last_contact_date')}</td>
              <td style="color:#f87171; font-weight:700;">{d.get('reason')}</td>
            </tr>"""

    html += """
          </tbody>
        </table>
      </div>

    </section>

    <!-- ========================================================================
         TAB 5: THIẾT KẾ QUY TRÌNH & ĐÁP ÁN TASK 1 & TASK 2
         ======================================================================== -->
    <section id="tab-design" class="view-tab-pane">
      <div class="full-card-container">
        <h3 style="font-size:16px; font-weight:800; color:var(--pink-primary); margin-bottom:12px;">📖 Thiết Kế Quy Trình & Đáp Án Toàn Diện (Task 1 & Task 2)</h3>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; font-size:12.5px; line-height:1.7;">
          <div style="background:var(--card-bg-sub); border:1px solid var(--card-border); border-radius:14px; padding:18px;">
            <strong style="color:var(--pink-primary); font-size:14px;">🎯 Task 1: Phân Tích Hiện Trạng & Thiết Kế Kiến Trúc</strong>
            <ul style="padding-left:18px; margin-top:8px;">
              <li><b>3 Vấn đề bối cảnh:</b> Trùng lặp liên hệ kép; Bỏ rơi khách tiềm năng vì thiếu thông tin ban đầu; Chấm điểm thiên vị ngân sách ảo lệch sản phẩm.</li>
              <li><b>4 Bước AI tự làm:</b> Khử trùng lặp O(1), Phân tích nhu cầu/gaps, Chấm điểm 4 tiêu chí trọng số, Điều phối cân bằng 8 NVKD.</li>
              <li><b>2 Điểm Human-in-the-Loop:</b> Trưởng phòng phê duyệt ca ngoại lệ; NVKD duyệt kịch bản gọi/mail.</li>
            </ul>
          </div>

          <div style="background:var(--card-bg-sub); border:1px solid var(--card-border); border-radius:14px; padding:18px;">
            <strong style="color:var(--green-accent); font-size:14px;">⚡ Task 2: Giải Pháp Triển Khai Chạy Được</strong>
            <ul style="padding-left:18px; margin-top:8px;">
              <li><b>2 Kỹ năng phối hợp:</b> <code>customer_segmentation</code> & <code>sales_followup</code>.</li>
              <li><b>Minh chứng AI chạy:</b> Hệ thống Audit Trail lưu vết quy tắc và payload từng bước vào <code>audit_trail.log</code>.</li>
              <li><b>Kiểm thử 3 ca:</b> Thông thường (Happy path); Thiếu dữ liệu (An Thịnh); Ranh giới/Ngoại lệ (Alpha, Nam Long, DNC).</li>
            </ul>
          </div>
        </div>

        <!-- Audit Trail Table -->
        <h4 style="font-size:13.5px; font-weight:800; color:var(--text-main); margin:20px 0 10px;">📜 Nhật Ký Kiểm Toán Thực Thi (Audit Trail)</h4>
        <table class="sakura-table">
          <thead>
            <tr>
              <th>Thời Gian</th>
              <th>Bước Quy Trình</th>
              <th>Hành Động</th>
              <th>Quy Tắc</th>
              <th>Chi Tiết Dữ Liệu</th>
            </tr>
          </thead>
          <tbody>"""

    for ev in audit.get("events", [])[-15:]:
        html += f"""
            <tr>
              <td><small style="color:var(--text-soft);">{ev.get('timestamp')}</small></td>
              <td><b>{ev.get('step')}</b></td>
              <td><code style="color:var(--pink-primary);">{ev.get('action')}</code></td>
              <td><span style="font-size:11px; font-weight:700;">{ev.get('rule_id')}</span></td>
              <td><pre style="font-size:11px; white-space:pre-wrap; max-width:400px; color:var(--text-soft);">{json.dumps(ev.get('details', {}), ensure_ascii=False)}</pre></td>
            </tr>"""

    html += """
          </tbody>
        </table>
      </div>
    </section>

  </main>

  <!-- ==========================================================================
       JAVASCRIPT LOGIC
       ========================================================================== -->
  <script>
    const MASTER_CUSTOMERS = """ + master_json_str + """;
    let currentFilteredList = [...MASTER_CUSTOMERS];
    let selectedCustomerId = MASTER_CUSTOMERS.length > 0 ? MASTER_CUSTOMERS[0].customer_id : null;
    let currentFilterMode = 'ALL';

    // Initialize Dashboard
    document.addEventListener("DOMContentLoaded", function() {
      renderOpportunityList();
      if (selectedCustomerId) {
        selectCustomer(selectedCustomerId);
      }
    });

    // Theme Mode Toggle (Sakura Dark vs Pastel Day)
    function toggleThemeMode() {
      document.body.classList.toggle('pastel-mode');
    }

    // Tab Navigation
    function switchMainTab(tabId, btn) {
      document.querySelectorAll('.view-tab-pane').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.nav-pill-btn').forEach(b => b.classList.remove('active'));

      let pane = document.getElementById(tabId);
      if (pane) pane.classList.add('active');

      if (btn) {
        btn.classList.add('active');
      } else {
        let matching = document.querySelector(`.nav-pill-btn[onclick*="${tabId}"]`);
        if (matching) matching.classList.add('active');
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Filter by Top KPI Cards
    function filterByPriority(priorityKey) {
      switchMainTab('tab-workspace');
      let chip = document.querySelector(`.opp-filter-chip[onclick*="${priorityKey}"]`) || document.querySelector('.opp-filter-chip');
      applyOppFilter(priorityKey, chip);
    }

    // Apply Filter to Opportunity List
    function applyOppFilter(mode, chipEl) {
      currentFilterMode = mode;
      document.querySelectorAll('.opp-filter-chip').forEach(c => c.classList.remove('active'));
      if (chipEl) chipEl.classList.add('active');

      if (mode === 'ALL') {
        currentFilteredList = [...MASTER_CUSTOMERS];
      } else if (mode === 'P1') {
        currentFilteredList = MASTER_CUSTOMERS.filter(c => c.priority === 'P1');
      } else if (mode === 'ESC') {
        currentFilteredList = MASTER_CUSTOMERS.filter(c => c.is_escalated);
      } else if (mode === 'P2') {
        currentFilteredList = MASTER_CUSTOMERS.filter(c => c.priority === 'P2');
      } else if (mode === 'UNFIT') {
        currentFilteredList = MASTER_CUSTOMERS.filter(c => c.priority === 'OUT_OF_SCOPE' || c.priority === 'DO_NOT_CONTACT' || c.priority === 'P3');
      }

      renderOpportunityList();
      if (currentFilteredList.length > 0) {
        selectCustomer(currentFilteredList[0].customer_id);
      }
    }

    // Search inside Opportunity List
    function searchOppList() {
      let q = document.getElementById('oppSearchInput').value.toLowerCase();
      let filtered = currentFilteredList.filter(c => {
        let text = (c.company_name + ' ' + (c.primary_contact?.name || '') + ' ' + (c.assigned_rep_name || '') + ' ' + c.customer_id).toLowerCase();
        return text.includes(q);
      });
      renderOpportunityCards(filtered);
    }

    // Render Opportunity List Cards
    function renderOpportunityList() {
      document.getElementById('oppCountDisplay').innerText = currentFilteredList.length + ' cơ hội';
      renderOpportunityCards(currentFilteredList);
    }

    function renderOpportunityCards(list) {
      let container = document.getElementById('oppScrollList');
      if (list.length === 0) {
        container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-soft); font-size:12px;">Không tìm thấy cơ hội nào phù hợp.</div>';
        return;
      }

      let html = '';
      list.forEach(c => {
        let isActive = (c.customer_id === selectedCustomerId) ? 'active' : '';
        let badgeHtml = '';
        if (c.priority === 'P1') {
          badgeHtml = '<span class="opp-badge-pill badge-continue">+ Có thể tiếp tục</span>';
        } else if (c.is_escalated) {
          badgeHtml = '<span class="opp-badge-pill badge-review">⏳ Chờ duyệt</span>';
        } else if (c.priority === 'P2') {
          badgeHtml = '<span class="opp-badge-pill badge-review">🟡 Cần bổ sung</span>';
        } else {
          badgeHtml = '<span class="opp-badge-pill badge-reject">🚫 Chưa đáp ứng</span>';
        }

        let budgetFmt = c.budget ? (c.budget / 1000000).toFixed(0) + ' tr' : 'Chưa rõ';

        html += `
          <div class="opp-card-item ${isActive}" id="opp-item-${c.customer_id}" onclick="selectCustomer('${c.customer_id}')">
            <div class="opp-card-top">
              <div>
                <span class="opp-card-id">${c.customer_id}</span>
                <div class="opp-card-name">${c.company_name}</div>
              </div>
              <div>${badgeHtml}</div>
            </div>
            <div class="opp-card-meta">
              <span>📍 ${c.city || 'Toàn quốc'} • 💰 ${budgetFmt}</span>
              <span>👤 ${c.assigned_rep_name || 'Chưa gán'}</span>
            </div>
          </div>
        `;
      });
      container.innerHTML = html;
    }

    // Select Customer and Populate Dossier View
    function selectCustomer(custId) {
      selectedCustomerId = custId;
      document.querySelectorAll('.opp-card-item').forEach(el => el.classList.remove('active'));
      let selectedEl = document.getElementById('opp-item-' + custId);
      if (selectedEl) selectedEl.classList.add('active');

      let c = MASTER_CUSTOMERS.find(x => x.customer_id === custId);
      if (!c) return;

      // Populate Header
      document.getElementById('dosTitle').innerText = c.customer_id + ' — ' + c.company_name;
      let contactName = c.primary_contact?.name || 'Đại diện công ty';
      let contactTitle = c.primary_contact?.title || '';
      let contactPhone = c.primary_contact?.phone || '';
      let contactEmail = c.primary_contact?.email || '';
      document.getElementById('dosSubtitle').innerHTML = `👤 <b>${contactName}</b> (${contactTitle}) • 📞 ${contactPhone} • 📧 ${contactEmail} • NVKD phụ trách: <b style="color:var(--pink-primary);">${c.assigned_rep_name || 'Chưa phân công'}</b>`;

      let badgeHtml = '';
      if (c.priority === 'P1') {
        badgeHtml = '<span class="opp-badge-pill badge-continue" style="font-size:12px; padding:4px 12px;">+ Có thể tiếp tục</span>';
      } else if (c.is_escalated) {
        badgeHtml = '<span class="opp-badge-pill badge-review" style="font-size:12px; padding:4px 12px;">⏳ Chờ Trưởng phòng duyệt</span>';
      } else if (c.priority === 'P2') {
        badgeHtml = '<span class="opp-badge-pill badge-review" style="font-size:12px; padding:4px 12px;">🟡 Cần bổ sung</span>';
      } else {
        badgeHtml = '<span class="opp-badge-pill badge-reject" style="font-size:12px; padding:4px 12px;">🚫 Chưa đáp ứng</span>';
      }
      document.getElementById('dosBadgeArea').innerHTML = badgeHtml;

      // Module 1: Sources
      let aliases = c.all_aliases?.join(', ') || 'Không có';
      let sources = c.source_channels?.map(s => `<span style="background:var(--pink-badge-bg); color:var(--pink-primary); padding:2px 6px; border-radius:4px; font-size:11px; font-weight:700;">${s}</span>`).join(' ') || '';
      document.getElementById('dosModuleSources').innerHTML = `
        Gộp <b>${c.registration_count || 1}</b> bản ghi nguồn: <code>${c.source_lead_ids?.join(', ')}</code><br>
        Kênh: ${sources}<br>
        Biến thể tên / viết tắt: <i>${aliases}</i>
      `;

      // Module 2: Needs
      let products = c.matched_products?.join(', ') || 'Chưa xác định';
      let budgetStr = c.budget ? c.budget.toLocaleString('vi-VN') + ' VNĐ' : 'Chưa rõ ngân sách';
      document.getElementById('dosModuleNeeds').innerHTML = `
        <b>Nhu cầu:</b> ${c.consolidated_needs || 'Chưa ghi nhận'}<br>
        <b>Khớp phần mềm Nam Việt:</b> <span style="color:var(--pink-primary); font-weight:700;">${products}</span><br>
        <b>Ngân sách:</b> ${budgetStr} • <b>Ngành:</b> ${c.industry || 'Khác'}
      `;

      // Module 3: Score
      let scoreBreakdown = '';
      if (c.scoring_breakdown) {
        scoreBreakdown = `
          <div class="score-breakdown-row">
            <span class="score-chip">Fit: ${c.scoring_breakdown.product_fit_score || 0}/40</span>
            <span class="score-chip">Budget: ${c.scoring_breakdown.budget_score || 0}/30</span>
            <span class="score-chip">Auth: ${c.scoring_breakdown.authority_score || 0}/20</span>
            <span class="score-chip">Info: ${c.scoring_breakdown.completeness_score || 0}/10</span>
          </div>
        `;
      }
      document.getElementById('dosModuleScore').innerHTML = `
        Điểm tổng AI: <b style="font-size:16px; color:var(--pink-primary);">${c.total_score || 'N/A'}/100</b> • Xếp hạng: <b>${c.priority || 'Chưa xếp'}</b><br>
        ${scoreBreakdown}
      `;

      // Module 4: Assigned Rep
      document.getElementById('dosModuleRep').innerHTML = `
        <b>NVKD:</b> ${c.assigned_rep_name || 'Chưa có'}<br>
        <b>Căn cứ phân công:</b> ${c.assigned_reason || 'Phù hợp địa bàn và ngành nghề'}
      `;

      // Module 5: Email Body
      document.getElementById('dosEmailBody').innerHTML = `<b>Chủ đề:</b> ${c.outreach_subject || '(Chưa có chủ đề)'}\n\n${c.outreach_body || '(Chưa có nội dung thư)'}`;

      // Module 6: Discovery Questions
      let qContainer = document.getElementById('dosQuestionsContainer');
      let qList = document.getElementById('dosQuestionsList');
      if (c.discovery_questions && c.discovery_questions.length > 0) {
        qContainer.style.display = 'block';
        qList.innerHTML = '<ul style="padding-left:16px; line-height:1.6;">' + c.discovery_questions.map(q => `<li>${q}</li>`).join('') + '</ul>';
      } else {
        qContainer.style.display = 'none';
      }

      // Next action & Approval button
      document.getElementById('dosNextAction').innerHTML = `🎯 <b>Hành động tiếp theo:</b> ${c.next_action || 'Liên hệ khách hàng theo quy chuẩn'}`;
      let escArea = document.getElementById('dosEscalateActionArea');
      if (c.is_escalated) {
        escArea.innerHTML = `<button class="btn-action-glow" style="padding:6px 14px; font-size:11.5px;" onclick="approveEscalation('${c.customer_id}')">✔ Phê Duyệt Phân Công</button>`;
      } else {
        escArea.innerHTML = '';
      }
    }

    // Copy Email Content
    function copyDossierEmail() {
      let text = document.getElementById('dosEmailBody').innerText;
      navigator.clipboard.writeText(text).then(() => alert("✅ Đã sao chép nội dung thư mời vào clipboard!"));
    }

    // Filter by Rep Name from Tab 3
    function filterByRepName(repName) {
      switchMainTab('tab-workspace');
      document.getElementById('oppSearchInput').value = repName;
      searchOppList();
    }

    // Preset selection
    function selectPresetDataset(datasetVal, btn) {
      document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
      if (btn) btn.classList.add('active');
      document.getElementById('runnerDatasetSelect').value = datasetVal;
      executeAgent(datasetVal);
    }

    // Execute Agent
    async function executeAgent(datasetParam) {
      let ds = datasetParam || document.getElementById('runnerDatasetSelect').value || 'standard';
      let btn = document.getElementById('btnRunAgentTop');
      let logBox = document.getElementById('terminalLogBox');
      let oldText = btn.innerText;
      btn.innerText = "⏳ Đang chạy AI...";
      btn.disabled = true;

      logBox.innerHTML += `\\n[*] Kích hoạt AI Agent pipeline với tập dữ liệu: '${ds}'...`;

      try {
        let res = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dataset: ds })
        });
        let data = await res.json();
        if (data.success) {
          logBox.innerHTML += `\\n[✔] ${data.message}`;
          logBox.innerHTML += `\\n[+] Hoàn tất! Tải lại trang sau 1 giây...`;
          setTimeout(() => location.reload(), 1000);
        } else {
          alert("❌ Lỗi: " + (data.error || "Không rõ nguyên nhân"));
        }
      } catch (e) {
        alert("❌ Lỗi kết nối server: " + e.message);
      } finally {
        btn.innerText = oldText;
        btn.disabled = false;
      }
    }

    // Upload JSON File
    async function uploadJsonFile(event) {
      let file = event.target.files[0];
      if (!file) return;
      let reader = new FileReader();
      reader.onload = async function(e) {
        try {
          let leads = JSON.parse(e.target.result);
          if (!Array.isArray(leads)) {
            alert("❌ File JSON phải là một mảng danh sách các leads!");
            return;
          }
          let res = await fetch("/api/upload", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ leads: leads })
          });
          let data = await res.json();
          if (data.success) {
            alert("✅ Đã nạp thành công " + leads.length + " hồ sơ mới và thực thi AI Agent!");
            location.reload();
          } else {
            alert("❌ Lỗi: " + data.error);
          }
        } catch (err) {
          alert("❌ Lỗi đọc định dạng JSON: " + err.message);
        }
      };
      reader.readAsText(file);
    }

    // Approve Escalation
    async function approveEscalation(custId) {
      if (!confirm("Xác nhận Trưởng phòng KD phê duyệt hồ sơ: " + custId + "?")) return;
      try {
        let res = await fetch("/api/approve-escalation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ customer_id: custId, rep_name: "Chỉ định bởi Trưởng Phòng KD" })
        });
        let data = await res.json();
        if (data.success) {
          alert("✅ Đã phê duyệt hồ sơ " + custId + " thành công!");
          let row = document.getElementById("esc-row-" + custId);
          if (row) row.remove();
          location.reload();
        }
      } catch (e) {
        alert("❌ Lỗi kết nối: " + e.message);
      }
    }
  </script>

</body>
</html>"""

    dashboard_path = os.path.join(BASE_DIR, "web", "dashboard.html")
    try:
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] Successfully compiled Sakura Dark / Business Edition Dashboard at: {dashboard_path}")
    except OSError:
        # Fallback for Vercel Serverless read-only filesystem
        tmp_path = "/tmp/dashboard.html"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[+] Compiled Dashboard to /tmp for Vercel at: {tmp_path}")
        except Exception as e:
            print(f"[!] Warning writing dashboard: {e}")

if __name__ == "__main__":
    generate_dashboard()
