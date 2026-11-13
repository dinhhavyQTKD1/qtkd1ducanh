"""
AI Agent Orchestrator for Nam Việt Software
Coordinates data ingestion, skill execution, decision trees, human-in-the-loop escalations, and output generation.
"""
import os
import json
import csv
from typing import List, Dict, Any

from config.settings import DATA_DIR, OUTPUTS_DIR, load_rules
from agent.audit_logger import AuditLogger
from skills.customer_segmentation import CustomerSegmentationSkill
from skills.sales_followup import SalesFollowupSkill

class NamVietAgentOrchestrator:
    def __init__(self, leads_file=None, history_file=None, sales_file=None, products_file=None, rules_file=None):
        self.rules = load_rules()
        self.logger = AuditLogger()
        
        # Load Data Files
        self.leads_file = leads_file or os.path.join(DATA_DIR, "leads_input.json")
        self.history_file = history_file or os.path.join(DATA_DIR, "contact_history.json")
        self.sales_file = sales_file or os.path.join(DATA_DIR, "sales_team.json")
        self.products_file = products_file or os.path.join(DATA_DIR, "products.json")

        self.raw_leads = self._load_json(self.leads_file)
        self.contact_history = self._load_json(self.history_file)
        self.sales_team = self._load_json(self.sales_file)
        self.products = self._load_json(self.products_file)

        # Initialize Skills
        self.segmentation_skill = CustomerSegmentationSkill(self.rules, self.products, self.logger)
        self.followup_skill = SalesFollowupSkill(self.sales_team, self.contact_history, self.rules, self.logger)

        self.logger.log(
            step="INITIALIZATION",
            action="LOAD_DATA_AND_RULES",
            rule_id="SYSTEM_INIT",
            details={
                "raw_leads_count": len(self.raw_leads),
                "history_records_count": len(self.contact_history),
                "sales_reps_count": len(self.sales_team),
                "products_count": len(self.products)
            }
        )

    def _load_json(self, file_path: str) -> Any:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def execute_pipeline(self) -> Dict[str, Any]:
        """
        Executes the entire end-to-end pipeline:
        Step 1: Deduplication & Entity Resolution
        Step 2: Needs & Gap Analysis
        Step 3: Lead Scoring & Prioritization
        Step 4: History Cross-check (DNC / Active clients)
        Step 5: Manager Escalation Detection
        Step 6: Smart Routing to 8 Sales Reps
        Step 7: Outreach Drafting & Question Formulation
        Step 8: Output Compilation & Reporting
        """
        print(f"\n>>> [1/7] Khởi động AI Agent. Bắt đầu đọc dữ liệu ({len(self.raw_leads)} leads thô)...")

        # 1. Deduplication & Entity Resolution
        master_customers = self.segmentation_skill.deduplicate_leads(self.raw_leads)
        print(f">>> [2/7] Đối chiếu & khử trùng hoàn tất: Từ {len(self.raw_leads)} bản ghi gộp thành {len(master_customers)} khách hàng duy nhất.")

        processed_customers = []
        sales_tasks = {rep["rep_id"]: [] for rep in self.sales_team}
        manager_escalations = []
        do_not_contact_list = []
        active_client_list = []

        print(f">>> [3/7] Phân tích nhu cầu, khoảng trống thông tin & chấm điểm ưu tiên...")
        for cust in master_customers:
            cust_id = cust["customer_id"]

            # 2. Needs & Gap Analysis
            gap_analysis = self.segmentation_skill.analyze_needs_and_gaps(cust)

            # 3. Lead Scoring & Prioritization
            scoring = self.segmentation_skill.score_customer(cust, gap_analysis)

            # 4. History Cross-Check
            history_match = self.followup_skill.check_contact_history(cust)

            # Check if Do Not Contact
            if history_match and history_match.get("status") == "DO_NOT_CONTACT":
                dnc_record = {
                    "customer_id": cust_id,
                    "company_name": cust["company_name"],
                    "contacts": cust["contacts"],
                    "status": "DO_NOT_CONTACT",
                    "reason": history_match.get("notes"),
                    "last_contact_date": history_match.get("last_contact_date")
                }
                do_not_contact_list.append(dnc_record)
                cust_record = {
                    **cust,
                    "gap_analysis": gap_analysis,
                    "scoring": scoring,
                    "priority": "DO_NOT_CONTACT",
                    "assigned_rep": "CHẶN LIÊN HỆ (DO NOT CALL)",
                    "rep_id": "DNC",
                    "next_action": "Tuyệt đối không gọi điện hoặc gửi email tiếp thị theo lịch sử yêu cầu của khách hàng.",
                    "is_escalated": False
                }
                processed_customers.append(cust_record)
                continue

            # Check if Active Client
            if history_match and history_match.get("status") == "ACTIVE_CLIENT":
                active_record = {
                    "customer_id": cust_id,
                    "company_name": cust["company_name"],
                    "contacts": cust["contacts"],
                    "status": "ACTIVE_CLIENT",
                    "notes": history_match.get("notes"),
                    "next_action": "Chuyển tiếp cho phòng CSKH / Quản lý Tài khoản (Account Manager), không tạo lead mới cho Sales."
                }
                active_client_list.append(active_record)
                cust_record = {
                    **cust,
                    "gap_analysis": gap_analysis,
                    "scoring": scoring,
                    "priority": "ACTIVE_CLIENT",
                    "assigned_rep": "BỘ PHẬN CSKH & ACCOUNT MANAGER",
                    "rep_id": "CSKH",
                    "next_action": active_record["next_action"],
                    "is_escalated": False
                }
                processed_customers.append(cust_record)
                continue

            # ----------------------------------------------------
            # BƯỚC 3 THEO SƠ ĐỒ WORKFLOW: QUYẾT ĐỊNH & PHÂN LOẠI
            # Điều kiện hình thoi: Khách có nhu cầu phù hợp & đủ thông tin?
            # ----------------------------------------------------
            has_suitable_need = not gap_analysis["is_out_of_scope"] and len(gap_analysis["matched_products"]) > 0
            has_sufficient_info = not gap_analysis["has_missing_info"]
            is_suitable_and_sufficient = has_suitable_need and has_sufficient_info

            if is_suitable_and_sufficient:
                workflow_decision = {
                    "branch": "CÓ",
                    "status": "Khách Tiềm Năng (Theo Ưu Tiên)",
                    "criteria_suitable_need": True,
                    "criteria_sufficient_info": True,
                    "action_strategy": "Mời Demo / Gửi tài liệu giải pháp phù hợp"
                }
            else:
                workflow_decision = {
                    "branch": "KHÔNG",
                    "status": "Cần bổ sung thông tin hoặc không liên hệ lại",
                    "criteria_suitable_need": has_suitable_need,
                    "criteria_sufficient_info": has_sufficient_info,
                    "action_strategy": "Hỏi thêm nhu cầu / Đưa vào danh sách chờ hoặc từ chối lịch sự"
                }

            # ----------------------------------------------------
            # BƯỚC 4 THEO SƠ ĐỒ WORKFLOW: PHÂN CÔNG & HÀNH ĐỘNG
            # ----------------------------------------------------
            # 5. Manager Escalation Detection
            escalation = self.followup_skill.check_escalation(cust, gap_analysis, history_match)

            # 6. Smart Sales Routing (Khớp Ngành + Khu vực, Cân bằng tải, Không trùng lặp)
            assignment = self.followup_skill.assign_sales_rep(cust)

            if not assignment.get("assigned"):
                # If rep cannot be found, escalate to manager
                if not escalation:
                    escalation = {
                        "is_escalated": True,
                        "reasons": [{
                            "code": "NO_MATCHING_SALES_REP",
                            "message": assignment["match_reason"]
                        }],
                        "action_required": "Trưởng phòng chỉ định nhân sự phù hợp cho khu vực/ngành này."
                    }

            # 7. Outreach & Discovery Questions Drafting (Mời Demo / Gửi tài liệu / Hỏi thêm nhu cầu)
            draft = self.followup_skill.generate_outreach_draft(cust, gap_analysis, scoring, assignment)

            # Build Full Record with explicit 6-step workflow alignment
            full_record = {
                "customer_id": cust_id,
                "company_name": cust["company_name"],
                "all_aliases": cust["all_company_aliases"],
                "source_lead_ids": cust["source_lead_ids"],
                "source_channels": cust["source_channels"],
                "registration_count": cust["registration_count"],
                "industry": cust["industry"],
                "city": cust["city"],
                "budget": cust["budget"],
                "company_size": cust["company_size"],
                "timeline": cust["timeline"],
                "consolidated_needs": cust["consolidated_needs"],
                "contacts": cust["contacts"],
                "primary_contact": cust["primary_contact"],
                
                # Step 2 & 3: AI Processing & Decision
                "matched_products": [p["product_name"] for p in gap_analysis["matched_products"]],
                "missing_information": gap_analysis["missing_fields"],
                "total_score": scoring["total_score"],
                "priority": scoring["priority"],
                "priority_label": scoring["priority_label"],
                "scoring_breakdown": scoring["breakdown"],
                "workflow_step_3_decision": workflow_decision,

                # Step 4: Assignment & Action
                "assigned_rep_id": assignment["rep_id"],
                "assigned_rep_name": assignment["rep_name"],
                "assigned_reason": assignment["match_reason"],
                "is_escalated": escalation is not None,
                "escalation_details": escalation if escalation else None,
                "next_action": draft["next_action"],
                "outreach_subject": draft["outreach_subject"],
                "outreach_body": draft["outreach_body"],
                "discovery_questions": draft["discovery_questions"],
                
                # Step 6: Human-in-the-loop audit check
                "human_check_required": escalation is not None or len(draft["discovery_questions"]) > 0
            }

            processed_customers.append(full_record)

            if escalation:
                manager_escalations.append({
                    "customer_id": cust_id,
                    "company_name": cust["company_name"],
                    "industry": cust["industry"],
                    "city": cust["city"],
                    "budget": cust["budget"],
                    "needs": cust["consolidated_needs"],
                    "contacts": cust["contacts"],
                    "escalation_reasons": escalation["reasons"],
                    "recommended_action": escalation["action_required"]
                })

            if assignment.get("assigned") and assignment["rep_id"] in sales_tasks:
                sales_tasks[assignment["rep_id"]].append({
                    "task_id": f"TASK-{cust_id}-{assignment['rep_id']}",
                    "customer_id": cust_id,
                    "company_name": cust["company_name"],
                    "priority": scoring["priority"],
                    "priority_label": scoring["priority_label"],
                    "contact_person": cust["primary_contact"].get("name"),
                    "contact_phone": cust["primary_contact"].get("phone"),
                    "contact_email": cust["primary_contact"].get("email"),
                    "inquired_needs": cust["consolidated_needs"],
                    "missing_info": gap_analysis["missing_fields"],
                    "next_action": draft["next_action"],
                    "outreach_draft_subject": draft["outreach_subject"],
                    "outreach_draft_body": draft["outreach_body"],
                    "discovery_questions": draft["discovery_questions"]
                })

        print(f">>> [4/7] Phân công cho 8 NVKD & Sàng lọc các ngoại lệ hoàn tất.")
        print(f">>> [5/7] Tạo báo cáo tổng hợp & Thống kê không đếm lặp...")

        # 8. Summary Report Compilation
        summary = self._compile_summary(processed_customers, sales_tasks, manager_escalations, do_not_contact_list, active_client_list)

        # 9. Save all artifacts to outputs/
        print(f">>> [6/7] Đang xuất toàn bộ dữ liệu ra thư mục outputs/...")
        self._save_outputs(processed_customers, sales_tasks, manager_escalations, do_not_contact_list, summary)

        # 10. Audit log completion
        self.logger.log(
            step="PIPELINE_COMPLETION",
            action="GENERATE_FINAL_OUTPUTS",
            rule_id="SYSTEM_DONE",
            details={
                "master_customers_count": len(processed_customers),
                "escalated_count": len(manager_escalations),
                "dnc_count": len(do_not_contact_list),
                "active_clients_count": len(active_client_list)
            }
        )
        self.logger.save_json()
        print(f">>> [7/7] Xong! Quy trình AI Agent hoàn thành xuất sắc 100%.")

        return {
            "master_customers": processed_customers,
            "sales_tasks": sales_tasks,
            "manager_escalations": manager_escalations,
            "do_not_contact": do_not_contact_list,
            "summary": summary
        }

    def _compile_summary(self, customers, sales_tasks, escalations, dnc_list, active_clients):
        # Priority distribution (distinct customers)
        priority_counts = {"P1": 0, "P2": 0, "P3": 0, "OUT_OF_SCOPE": 0, "DO_NOT_CONTACT": 0, "ACTIVE_CLIENT": 0, "UNQUALIFIED": 0}
        for c in customers:
            p = c.get("priority", "UNQUALIFIED")
            priority_counts[p] = priority_counts.get(p, 0) + 1

        # Sales Rep distribution
        rep_counts = {}
        for rep in self.sales_team:
            rep_id = rep["rep_id"]
            tasks = sales_tasks.get(rep_id, [])
            rep_counts[rep["name"]] = {
                "rep_id": rep_id,
                "industries": rep["industries"],
                "region": rep["regions"],
                "assigned_leads_count": len(tasks),
                "p1_hot": sum(1 for t in tasks if t["priority"] == "P1"),
                "p2_warm": sum(1 for t in tasks if t["priority"] == "P2"),
                "p3_cold": sum(1 for t in tasks if t["priority"] == "P3")
            }

        return {
            "total_raw_leads_ingested": len(self.raw_leads),
            "total_master_customers_unique": len(customers),
            "deduplication_reduction_rate": f"{((len(self.raw_leads) - len(customers)) / len(self.raw_leads) * 100):.1f}%" if len(self.raw_leads) > 0 else "0%",
            "priority_breakdown_unique": priority_counts,
            "escalations_to_sales_manager": len(escalations),
            "do_not_contact_blocked": len(dnc_list),
            "existing_clients_routed_to_cskh": len(active_clients),
            "sales_rep_workload_distribution": rep_counts
        }

    def _save_outputs(self, customers, sales_tasks, escalations, dnc_list, summary):
        # 1. Master Customers JSON
        with open(os.path.join(OUTPUTS_DIR, "master_customers.json"), "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)

        # 2. Master Customers CSV
        with open(os.path.join(OUTPUTS_DIR, "master_customers.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Mã KH (Customer ID)", "Tên Doanh Nghiệp", "Số bản ghi gộp", "Nguồn", "Lĩnh Vực",
                "Tỉnh/Khu Vực", "Ngân Sách (VNĐ)", "Mức Ưu Tiên", "Điểm Đánh Giá",
                "NVKD Đề Xuất", "Người Liên Hệ Chính", "SĐT", "Email", "Việc Cần Làm Tiếp"
            ])
            for c in customers:
                writer.writerow([
                    c.get("customer_id"),
                    c.get("company_name"),
                    c.get("registration_count"),
                    ", ".join(c.get("source_channels", [])),
                    c.get("industry"),
                    c.get("city"),
                    f"{c.get('budget'):,.0f}" if c.get("budget") else "Chưa rõ",
                    c.get("priority_label", c.get("priority")),
                    c.get("total_score", "N/A"),
                    c.get("assigned_rep_name", c.get("assigned_rep")),
                    c.get("primary_contact", {}).get("name", ""),
                    c.get("primary_contact", {}).get("phone", ""),
                    c.get("primary_contact", {}).get("email", ""),
                    c.get("next_action")
                ])

        # 3. Sales Task Assignments JSON
        with open(os.path.join(OUTPUTS_DIR, "sales_task_assignments.json"), "w", encoding="utf-8") as f:
            json.dump(sales_tasks, f, ensure_ascii=False, indent=2)

        # 4. Sales Task Assignments CSV
        with open(os.path.join(OUTPUTS_DIR, "sales_task_assignments.csv"), "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Mã Công Việc", "Mã NVKD", "Tên NVKD", "Mã KH", "Tên Khách Hàng",
                "Mức Ưu Tiên", "Người Liên Hệ", "Số Điện Thoại", "Hành Động Đề Xuất", "Tiêu Đề Email Dự Thảo"
            ])
            for rep in self.sales_team:
                rep_id = rep["rep_id"]
                tasks = sales_tasks.get(rep_id, [])
                for t in tasks:
                    writer.writerow([
                        t["task_id"],
                        rep_id,
                        rep["name"],
                        t["customer_id"],
                        t["company_name"],
                        t["priority_label"],
                        t["contact_person"],
                        t["contact_phone"],
                        t["next_action"],
                        t["outreach_draft_subject"]
                    ])

        # 5. Manager Escalations JSON
        with open(os.path.join(OUTPUTS_DIR, "manager_escalations.json"), "w", encoding="utf-8") as f:
            json.dump(escalations, f, ensure_ascii=False, indent=2)

        # 6. Do Not Contact JSON
        with open(os.path.join(OUTPUTS_DIR, "do_not_contact.json"), "w", encoding="utf-8") as f:
            json.dump(dnc_list, f, ensure_ascii=False, indent=2)

        # 7. Summary Report JSON
        with open(os.path.join(OUTPUTS_DIR, "summary_report.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 8. Summary Report Markdown
        md_content = self._render_markdown_summary(summary)
        with open(os.path.join(OUTPUTS_DIR, "summary_report.md"), "w", encoding="utf-8") as f:
            f.write(md_content)

    def _render_markdown_summary(self, summary: dict) -> str:
        md = f"""# BÁO CÁO TỔNG HỢP ĐIỀU PHỐI KHÁCH HÀNG TIỀM NĂNG
## CÔNG TY PHẦN MỀM NAM VIỆT - HỆ THỐNG AI AGENT ĐIỀU PHỐI (AI301 - ĐỀ 02)

---

### 1. Tổng Quan Chỉ Số Xử Lý (Lead Processing Metrics)
- **Tổng số hồ sơ tiếp nhận ban đầu (Raw Leads):** `{summary['total_raw_leads_ingested']}` hồ sơ.
- **Tổng số khách hàng duy nhất sau khử trùng (Master Customers):** `{summary['total_master_customers_unique']}` doanh nghiệp.
- **Tỷ lệ giảm tải trùng lặp (Deduplication Rate):** `{summary['deduplication_reduction_rate']}`.
- **Số hồ sơ chuyển Trưởng phòng Kinh doanh xem xét (Escalations):** `{summary['escalations_to_sales_manager']}` khách hàng.
- **Số hồ sơ chặn theo lịch sử (Do Not Contact):** `{summary['do_not_contact_blocked']}` khách hàng.
- **Số khách hàng hiện hữu chuyển sang CSKH/Account Manager:** `{summary['existing_clients_routed_to_cskh']}` khách hàng.

---

### 2. Phân Bổ Mức Độ Ưu Tiên (Khách Hàng Duy Nhất - Không Đếm Lặp)
| Phân loại ưu tiên | Ý nghĩa nghiệp vụ | Số lượng (KH duy nhất) | Tỷ lệ (%) |
| :--- | :--- | :---: | :---: |
| **P1 - Hot Lead** | Nhu cầu khớp sản phẩm, ngân sách chuẩn, liên hệ cấp lãnh đạo (Cần gọi trong 2h) | `{summary['priority_breakdown_unique'].get('P1', 0)}` | `{(summary['priority_breakdown_unique'].get('P1', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |
| **P2 - Warm Lead** | Nhu cầu rất phù hợp, cần phỏng vấn bổ sung thông tin thiếu (Gọi trong 8h) | `{summary['priority_breakdown_unique'].get('P2', 0)}` | `{(summary['priority_breakdown_unique'].get('P2', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |
| **P3 - Cold Lead** | Nhu cầu chung chung / vãng lai, gửi tài liệu cẩm nang nuôi dưỡng | `{summary['priority_breakdown_unique'].get('P3', 0)}` | `{(summary['priority_breakdown_unique'].get('P3', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |
| **Out-of-Scope** | Ngân sách lớn hoặc yêu cầu ngoài dòng sản phẩm Nam Việt (Gia công, Drone...) | `{summary['priority_breakdown_unique'].get('OUT_OF_SCOPE', 0)}` | `{(summary['priority_breakdown_unique'].get('OUT_OF_SCOPE', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |
| **Do Not Contact** | Khách hàng lịch sử yêu cầu không làm phiền / Blacklist (Tuyệt đối không gọi) | `{summary['priority_breakdown_unique'].get('DO_NOT_CONTACT', 0)}` | `{(summary['priority_breakdown_unique'].get('DO_NOT_CONTACT', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |
| **Active Client** | Khách hàng hiện hữu cần mở rộng / hỗ trợ dịch vụ -> Chuyển CSKH | `{summary['priority_breakdown_unique'].get('ACTIVE_CLIENT', 0)}` | `{(summary['priority_breakdown_unique'].get('ACTIVE_CLIENT', 0) / summary['total_master_customers_unique'] * 100):.1f}%` |

---

### 3. Phân Phối Tải Công Việc Cho 8 Nhân Viên Kinh Doanh (Không Đếm Lặp)
| Mã NVKD | Họ và tên NVKD | Nhóm ngành phụ trách | Khu vực | Tổng số KH nhận | P1 (Hot) | P2 (Warm) | P3 (Cold) |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
"""
        for name, data in summary["sales_rep_workload_distribution"].items():
            md += f"| `{data['rep_id']}` | **{name}** | {', '.join(data['industries'])} | {', '.join(data['region'])} | **{data['assigned_leads_count']}** | {data['p1_hot']} | {data['p2_warm']} | {data['p3_cold']} |\n"

        md += """
---
*Báo cáo được tự động khởi tạo bởi NamViet AI Lead Dispatcher Engine.*
"""
        return md

