"""
Main Entry Point for Nam Việt Software AI Agent
AI301 - Đề án 02: AI Agent Sàng lọc và Điều phối Khách hàng Tiềm năng
"""
import sys
import os
import argparse
import json

from config.settings import BASE_DIR, DATA_DIR, OUTPUTS_DIR
from agent.orchestrator import NamVietAgentOrchestrator
from web.generate_dashboard import generate_dashboard

# Vercel entrypoint compatibility
try:
    from server import app, application, handler
except Exception:
    app = None
    application = None
    handler = None

def main():
    parser = argparse.ArgumentParser(description="Nam Việt AI Agent Sàng lọc & Điều phối Khách hàng")
    parser.add_argument("--leads", type=str, default=None, help="Đường dẫn file leads đầu vào (JSON)")
    parser.add_argument("--history", type=str, default=None, help="Đường dẫn file lịch sử liên hệ (JSON)")
    parser.add_argument("--sales", type=str, default=None, help="Đường dẫn file danh sách nhân viên kinh doanh (JSON)")
    parser.add_argument("--products", type=str, default=None, help="Đường dẫn file danh mục sản phẩm (JSON)")
    args = parser.parse_args()

    print("=" * 80)
    print("      CÔNG TY CỔ PHẦN PHẦN MỀM NAM VIỆT - GROW TOGETHER")
    print("      HỆ THỐNG AI AGENT SÀNG LỌC & ĐIỀU PHỐI KHÁCH HÀNG TIỀM NĂNG")
    print("      Đồ án AI301 - Đề số 02")
    print("=" * 80)

    orchestrator = NamVietAgentOrchestrator(
        leads_file=args.leads,
        history_file=args.history,
        sales_file=args.sales,
        products_file=args.products
    )

    results = orchestrator.execute_pipeline()
    summary = results["summary"]
    generate_dashboard()

    print("\n" + "=" * 80)
    print("                     KẾT QUẢ THỐNG KÊ TỔNG HỢP")
    print("=" * 80)
    print(f"[*] Tổng hồ sơ đầu vào tiếp nhận:         {summary['total_raw_leads_ingested']} hồ sơ")
    print(f"[*] Tổng khách hàng duy nhất sau gộp:      {summary['total_master_customers_unique']} khách hàng (Giảm {summary['deduplication_reduction_rate']})")
    print(f"[*] Khách hàng Hot Lead (P1):              {summary['priority_breakdown_unique'].get('P1', 0)} khách hàng")
    print(f"[*] Khách hàng Warm Lead (P2):             {summary['priority_breakdown_unique'].get('P2', 0)} khách hàng")
    print(f"[*] Khách hàng Cold Lead (P3):             {summary['priority_breakdown_unique'].get('P3', 0)} khách hàng")
    print(f"[*] Khách ngoài phạm vi (Out-of-Scope):    {summary['priority_breakdown_unique'].get('OUT_OF_SCOPE', 0)} khách hàng")
    print(f"[*] Chặn liên hệ theo lịch sử (DNC):       {summary['do_not_contact_blocked']} khách hàng")
    print(f"[*] Khách hàng hiện hữu (Chuyển CSKH):     {summary['existing_clients_routed_to_cskh']} khách hàng")
    print(f"[*] Chuyển Trưởng phòng KD quyết định:     {summary['escalations_to_sales_manager']} trường hợp")
    print("-" * 80)
    print("PHÂN CÔNG CÔNG VIỆC CHO 8 NHÂN VIÊN KINH DOANH (KHÔNG ĐẾM LẶP):")
    for name, data in summary["sales_rep_workload_distribution"].items():
        print(f"  - [{data['rep_id']}] {name:<18} ({', '.join(data['industries']):<28} | {', '.join(data['region']):<10}): "
              f"Nhận {data['assigned_leads_count']:2d} KH (P1: {data['p1_hot']}, P2: {data['p2_warm']}, P3: {data['p3_cold']})")
    print("=" * 80)
    print(f"[+] Các file kết quả đã được xuất tại thư mục: {OUTPUTS_DIR}")
    print(f"    1. master_customers.json / .csv       (Hồ sơ hợp nhất & bản nháp tiếp cận)")
    print(f"    2. sales_task_assignments.json / .csv (Danh sách công việc chi tiết cho 8 Sales)")
    print(f"    3. manager_escalations.json           (Danh sách chuyển Trưởng phòng quyết định)")
    print(f"    4. do_not_contact.json                (Danh sách chặn gọi)")
    print(f"    5. summary_report.json / .md          (Báo cáo tổng hợp số liệu)")
    print(f"    6. audit_trail.log / execution_log.json (Nhật ký truy vết quy tắc)")
    print("=" * 80)

if __name__ == "__main__":
    main()
