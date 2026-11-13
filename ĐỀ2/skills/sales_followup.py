"""
Skill: sales_followup
Responsibilities:
1. Cross-check contact history (Do-Not-Contact blacklist, Active Clients, Prior Complaints).
2. Smart sales routing & workload balancing across the 8 Sales Representatives.
3. Identify manager escalation triggers.
4. Auto-generate personalized outreach messages and discovery questionnaires based on information gaps.
"""
import re
from typing import List, Dict, Any, Optional

class SalesFollowupSkill:
    def __init__(self, sales_team: List[Dict[str, Any]], contact_history: List[Dict[str, Any]], rules: Dict[str, Any], logger=None):
        self.sales_team = sales_team
        self.contact_history = contact_history
        self.rules = rules
        self.logger = logger
        self.escalation_cfg = rules.get("escalation", {})

    def normalize_phone(self, phone: str) -> str:
        if not phone:
            return ""
        clean = re.sub(r"[^\d]", "", str(phone))
        if clean.startswith("84") and len(clean) >= 11:
            clean = "0" + clean[2:]
        return clean

    # ---------------------------
    # 1. HISTORY CROSS-CHECK
    # ---------------------------
    def check_contact_history(self, customer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cust_phones = [self.normalize_phone(c.get("phone")) for c in customer.get("contacts", []) if c.get("phone")]
        cust_emails = [(c.get("email") or "").strip().lower() for c in customer.get("contacts", []) if c.get("email")]
        cust_company = (customer.get("company_name") or "").lower()

        for h in self.contact_history:
            h_phone = self.normalize_phone(h.get("phone"))
            h_email = (h.get("email") or "").strip().lower()
            h_company = (h.get("company_name") or "").lower()

            matched = False
            if h_phone and h_phone in cust_phones:
                matched = True
            elif h_email and h_email in cust_emails:
                matched = True
            elif h_company and (h_company in cust_company or cust_company in h_company) and len(h_company) > 10:
                matched = True

            if matched:
                status = h.get("status")
                notes = h.get("notes", "")
                result = {
                    "matched_history": True,
                    "status": status,
                    "notes": notes,
                    "last_contact_date": h.get("last_contact_date")
                }
                if self.logger:
                    self.logger.log(
                        step="HISTORY_CROSS_CHECK",
                        action="HISTORY_MATCH_FOUND",
                        rule_id=f"RULE_HISTORY_{status}",
                        details={
                            "customer_id": customer["customer_id"],
                            "company_name": customer["company_name"],
                            "matched_status": status,
                            "notes": notes
                        }
                    )
                return result

        return None

    # ---------------------------
    # 2. ESCALATION DETECTION
    # ---------------------------
    def check_escalation(self, customer: Dict[str, Any], gap_analysis: Dict[str, Any], history_check: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        reasons = []

        # Trigger 1: Contact History Complaints
        if history_check and history_check.get("status") == "COMPLAINT_PENDING":
            reasons.append({
                "code": "PREVIOUS_COMPLAINT_HISTORY",
                "message": f"Khách hàng có lịch sử khiếu nại trước đó: {history_check.get('notes')}"
            })

        # Trigger 2: High Budget with Unclear Requirements or Scope
        high_budget_threshold = self.escalation_cfg.get("high_budget_unclear_threshold", 200000000)
        budget = customer.get("budget") or 0
        if budget >= high_budget_threshold and (gap_analysis.get("has_missing_info") or len(gap_analysis.get("matched_products", [])) == 0):
            reasons.append({
                "code": "HIGH_BUDGET_UNCLEAR_REQUIREMENTS",
                "message": f"Ngân sách lớn ({budget:,.0f} VNĐ) nhưng yêu cầu phạm vi chưa rõ ràng hoặc thiếu thông số kỹ thuật then chốt."
            })

        # Trigger 3: Multi-region Enterprise
        city = (customer.get("city") or "").lower()
        if any(k in city for k in ["đa chi nhánh", "toàn quốc", "bắc", "nam", "trung"]) and len(re.findall(r"(hà nội|đà nẵng|hồ chí minh|tp\.hcm)", city)) > 1:
            reasons.append({
                "code": "MULTI_REGION_ENTERPRISE",
                "message": f"Doanh nghiệp quy mô lớn hoạt động đa chi nhánh ({customer.get('city')}), cần Trưởng phòng chỉ định tổ công tác liên vùng."
            })

        # Trigger 4: Out-of-scope but High Potential Custom Request
        if gap_analysis.get("is_out_of_scope") and budget >= 1000000000:
            reasons.append({
                "code": "OUT_OF_SCOPE_POTENTIAL_CUSTOM",
                "message": f"Yêu cầu nằm ngoài giải pháp đóng gói chuẩn của Nam Việt nhưng ngân sách rất cao ({budget:,.0f} VNĐ), cần xem xét chuyển giao đối tác hệ sinh thái."
            })

        if reasons:
            escalation_info = {
                "is_escalated": True,
                "reasons": reasons,
                "action_required": "Trưởng phòng Kinh doanh xem xét trực tiếp và phê duyệt phương án tiếp cận."
            }
            if self.logger:
                self.logger.log(
                    step="ESCALATION_CHECK",
                    action="TRIGGER_MANAGER_ESCALATION",
                    rule_id=reasons[0]["code"],
                    details={
                        "customer_id": customer["customer_id"],
                        "reasons": [r["message"] for r in reasons]
                    }
                )
            return escalation_info

        return None

    # ---------------------------
    # 3. SMART SALES ROUTING
    # ---------------------------
    def assign_sales_rep(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        cust_industry = (customer.get("industry") or "").lower()
        cust_city = (customer.get("city") or "").lower()

        # Map city to Region
        north_provinces = ["hà nội", "hải phòng", "quảng ninh", "bắc ninh", "vĩnh phúc", "hải dương", "hưng yên", "hà nam", "nam định", "thái bình", "lào cai", "bắc"]
        central_provinces = ["đà nẵng", "huế", "quảng nam", "quảng ngãi", "bình định", "khánh hòa", "nghệ an", "hà tĩnh", "thanh hóa", "nha trang", "trung", "lâm đồng", "đắk lắk", "gia lai"]
        south_provinces = ["hồ chí minh", "tp.hcm", "tp. hồ chí minh", "bình dương", "đồng nai", "long an", "bà rịa", "vũng tàu", "cần thơ", "tiền giang", "tây ninh", "nam"]

        target_region = None
        if any(p in cust_city for p in north_provinces):
            target_region = "Miền Bắc"
        elif any(p in cust_city for p in central_provinces):
            target_region = "Miền Trung"
        elif any(p in cust_city for p in south_provinces):
            target_region = "Miền Nam"

        candidates = []
        for rep in self.sales_team:
            # Check Industry match
            industry_match = False
            for ind in rep["industries"]:
                if ind.lower() in cust_industry or cust_industry in ind.lower():
                    industry_match = True
                    break

            # Check Region / Province match
            region_match = False
            if target_region and target_region in rep["regions"]:
                region_match = True
            elif "Toàn quốc" in rep["regions"]:
                region_match = True
            for prov in rep.get("provinces", []):
                if prov.lower() in cust_city:
                    region_match = True
                    break

            if industry_match and region_match:
                candidates.append(rep)

        # Workload balancing & selection
        if candidates:
            # Sort by current workload (ascending)
            candidates.sort(key=lambda r: (r["current_load"], -r["max_capacity"]))
            chosen = candidates[0]
            chosen["current_load"] += 1
            
            assignment = {
                "assigned": True,
                "rep_id": chosen["rep_id"],
                "rep_name": chosen["name"],
                "rep_email": chosen["email"],
                "rep_phone": chosen["phone"],
                "match_reason": f"Khớp ngành phụ trách ({', '.join(chosen['industries'])}) và khu vực ({target_region or customer.get('city')}). Tải hiện tại: {chosen['current_load']}/{chosen['max_capacity']}"
            }
        else:
            # Fallback: check general rep or flag as unassigned
            general_reps = [r for r in self.sales_team if "Toàn quốc" in r["regions"] or "Dịch vụ tổng hợp" in r["industries"]]
            if general_reps and target_region in ["Miền Trung", "Miền Nam"]:
                general_reps.sort(key=lambda r: r["current_load"])
                chosen = general_reps[0]
                chosen["current_load"] += 1
                assignment = {
                    "assigned": True,
                    "rep_id": chosen["rep_id"],
                    "rep_name": chosen["name"],
                    "rep_email": chosen["email"],
                    "rep_phone": chosen["phone"],
                    "match_reason": f"Gán cho nhân viên linh hoạt phụ trách bổ sung ({chosen['name']}) do ngành/vùng đặc thù. Tải hiện tại: {chosen['current_load']}"
                }
            else:
                assignment = {
                    "assigned": False,
                    "rep_id": "UNASSIGNED",
                    "rep_name": "Chưa có nhân sự phù hợp",
                    "rep_email": "",
                    "rep_phone": "",
                    "match_reason": f"Chưa có nhân sự phụ trách phù hợp cho ngành '{customer.get('industry')}' tại khu vực '{customer.get('city')}'. Đưa vào danh sách Trưởng phòng quyết định."
                }

        if self.logger:
            self.logger.log(
                step="SALES_ROUTING",
                action="ASSIGN_SALES_REP",
                rule_id="RULE_ROUTING_INDUSTRY_REGION",
                details={
                    "customer_id": customer["customer_id"],
                    "assigned_rep": assignment["rep_name"],
                    "reason": assignment["match_reason"]
                }
            )

        return assignment

    # ---------------------------
    # 4. OUTREACH DRAFTING
    # ---------------------------
    def generate_outreach_draft(self, customer: Dict[str, Any], gap_analysis: Dict[str, Any], scoring: Dict[str, Any], assignment: Dict[str, Any]) -> Dict[str, Any]:
        contact = customer.get("primary_contact", {})
        c_name = contact.get("name") or "Quý Khách Hàng"
        c_title = contact.get("title") or "Quý Doanh Nghiệp"
        company = customer.get("company_name", "Quý Công ty")
        priority = scoring.get("priority")
        matched_prods = gap_analysis.get("matched_products", [])
        primary_prod_name = matched_prods[0]["product_name"] if matched_prods else "Giải pháp Quản trị Doanh nghiệp Nam Việt"
        rep_name = assignment.get("rep_name", "Chuyên viên Nam Việt")
        rep_phone = assignment.get("rep_phone", "1900-6868")

        missing_fields = gap_analysis.get("missing_fields", [])
        discovery_questions = []
        for field in missing_fields:
            if "Ngân sách" in field:
                discovery_questions.append("Quý doanh nghiệp dự kiến mức ngân sách đầu tư cho dự án phần mềm này trong khoảng nào để Nam Việt thiết kế gói phù hợp?")
            elif "Email" in field:
                discovery_questions.append("Anh/Chị vui lòng chia sẻ thêm địa chỉ Email làm việc chính thức để Nam Việt gửi trọn bộ tài liệu giải pháp và demo?")
            elif "Quy mô" in field:
                discovery_questions.append("Hiện tại số lượng nhân sự hoặc số điểm bán hàng/phòng ban của công ty mình là bao nhiêu?")
            elif "Lộ trình" in field:
                discovery_questions.append("Thời điểm anh/chị dự kiến bắt đầu ứng dụng giải pháp là khi nào (ngay trong tháng hay quý tới)?")

        if priority == "P1":
            subject = f"[Nam Việt] Thư mời trải nghiệm Demo Giải pháp {primary_prod_name} dành riêng cho {company}"
            body = (
                f"Kính gửi {c_title} {c_name},\n\n"
                f"Em là {rep_name} - Chuyên viên Tư vấn Giải pháp Quản trị Doanh nghiệp tại Nam Việt Software.\n"
                f"Được biết {company} đang có nhu cầu tối ưu hóa vận hành thông qua {primary_prod_name}, "
                f"đặc biệt trong việc {customer.get('consolidated_needs')}.\n\n"
                f"Nam Việt đã đồng hành cùng nhiều doanh nghiệp trong ngành {customer.get('industry')} và giúp nâng cao 35% hiệu suất quản lý. "
                f"Em trân trọng kính mời Anh/Chị một buổi chia sẻ ngắn (khoảng 30 phút trực tiếp hoặc online) để đội ngũ chuyên gia Nam Việt "
                f"trình bày trực tiếp mô hình ứng dụng thực tế trên quy mô của {company}.\n\n"
                f"Anh/Chị thuận tiện vào sáng thứ Năm hay chiều thứ Sáu tuần này để em sắp xếp lịch chuẩn bị chu đáo nhất ạ?\n\n"
                f"Trân trọng,\n"
                f"{rep_name} | Nam Việt Software\nHotline: {rep_phone}"
            )
            next_action = f"Gọi điện xác nhận lịch hẹn Demo 1-1 với {c_name} ({contact.get('phone')}) trong vòng 2 giờ."

        elif priority == "P2":
            subject = f"[Nam Việt] Tư vấn chuyên sâu & Khảo sát nhu cầu giải pháp quản trị cho {company}"
            questions_text = "\n".join([f"  - {q}" for q in discovery_questions]) if discovery_questions else "  - Mong muốn trọng tâm cần giải quyết trong giai đoạn này là gì?"
            body = (
                f"Kính gửi {c_title} {c_name},\n\n"
                f"Em là {rep_name} đến từ Nam Việt Software. "
                f"Cảm ơn Anh/Chị đã quan tâm và để lại yêu cầu tư vấn về {customer.get('consolidated_needs')}.\n\n"
                f"Để đội ngũ kỹ sư giải pháp Nam Việt có thể xây dựng bản đề xuất kiến trúc và báo giá tối ưu nhất cho {company}, "
                f"em xin phép trao đổi nhanh một số thông tin trọng tâm sau ạ:\n"
                f"{questions_text}\n\n"
                f"Em sẽ chủ động liên hệ qua điện thoại {contact.get('phone')} để lắng nghe kỹ hơn mong muốn của Anh/Chị.\n\n"
                f"Trân trọng,\n"
                f"{rep_name} | Nam Việt Software\nHotline: {rep_phone}"
            )
            next_action = f"Liên hệ phỏng vấn khám phá nhu cầu (Discovery Call) và thu thập thông tin còn thiếu trong vòng 8 giờ."

        elif priority == "P3":
            subject = f"[Nam Việt] Bộ tài liệu cẩm nang chuyển đổi số và quản trị doanh nghiệp hiệu quả"
            body = (
                f"Kính gửi {c_title} {c_name},\n\n"
                f"Em là {rep_name} từ Nam Việt Software. "
                f"Xin cảm ơn Anh/Chị đã gửi thông tin tìm hiểu về giải pháp của chúng em.\n\n"
                f"Em xin gửi tặng Anh/Chị bộ tài liệu giới thiệu chi tiết về hệ sinh thái phần mềm quản trị Nam Việt (CRM, HRM, ERP, Kế toán). "
                f"Khi nào doanh nghiệp có kế hoạch triển khai cụ thể, Anh/Chị chỉ cần phản hồi email này hoặc liên hệ hotline để được hỗ trợ tức thì.\n\n"
                f"Trân trọng,\n"
                f"{rep_name} | Nam Việt Software"
            )
            next_action = "Gửi email tài liệu tổng quan và đưa vào kịch bản nuôi dưỡng định kỳ (Email Nurturing Flow)."

        elif priority == "OUT_OF_SCOPE":
            subject = f"[Nam Việt] Thư cảm ơn và phản hồi thông tin tư vấn kỹ thuật"
            body = (
                f"Kính gửi {c_title} {c_name},\n\n"
                f"Nam Việt Software trân trọng cảm ơn Anh/Chị và {company} đã quan tâm liên hệ.\n\n"
                f"Sau khi đánh giá yêu cầu ({customer.get('consolidated_needs')}), bộ phận kỹ thuật Nam Việt nhận thấy nhu cầu của đơn vị mình "
                f"thuộc lĩnh vực chuyên biệt ngoài phạm vi các sản phẩm quản trị SME chuẩn của chúng em. "
                f"Để đảm bảo chất lượng dự án tốt nhất cho {company}, chúng em xin phép ghi nhận và sẽ kết nối Anh/Chị với đối tác chuyên môn phù hợp trong mạng lưới liên minh chuyển đổi số.\n\n"
                f"Trân trọng,\n"
                f"Ban Tư vấn Giải pháp - Nam Việt Software"
            )
            next_action = "Lưu hồ sơ đối tác tiềm năng, không đưa vào KPI gọi bán lẻ."

        else:
            subject = f"[Nam Việt] Thông báo tiếp nhận thông tin yêu cầu dịch vụ"
            body = f"Kính gửi {company},\nNam Việt đã tiếp nhận yêu cầu và đang phân công chuyên viên liên hệ trong thời gian sớm nhất."
            next_action = "Chờ Trưởng phòng phê duyệt hướng xử lý."

        return {
            "outreach_subject": subject,
            "outreach_body": body,
            "discovery_questions": discovery_questions,
            "next_action": next_action
        }

