"""
Automated Test Suite for Nam Việt AI Agent
Evaluates:
1. Standard Cases (Happy Path)
2. Missing Data Cases (Information Gaps & Premature Abandonment Prevention)
3. Boundary & Edge Cases (DNC, Out-of-Scope, Deduplication, Escalations)
Runs cleanly on any standard Python 3 runtime without external dependencies.
"""
import sys
import os
import json
import time

from config.settings import load_rules
from agent.orchestrator import NamVietAgentOrchestrator
from skills.customer_segmentation import CustomerSegmentationSkill
from skills.sales_followup import SalesFollowupSkill

class SimpleTestRunner:
    def __init__(self):
        self.rules = load_rules()
        self.products = [
            {
                "product_id": "PROD-CRM",
                "name": "NamViet CRM Pro",
                "category": "Quản lý Bán hàng & Chăm sóc Khách hàng",
                "target_industry": ["Bán lẻ"],
                "min_budget": 15000000,
                "max_budget": 120000000,
                "keywords": ["crm", "khách hàng", "bán hàng"]
            },
            {
                "product_id": "PROD-ERP",
                "name": "NamViet ERP SMB",
                "category": "Hệ thống ERP tổng thể",
                "target_industry": ["Sản xuất"],
                "min_budget": 80000000,
                "max_budget": 450000000,
                "keywords": ["erp", "sản xuất", "kho", "định mức"]
            }
        ]
        self.sales_team = [
            {
                "rep_id": "SALE-01",
                "name": "Nguyễn Văn An",
                "email": "an.nguyen@namviet-software.vn",
                "phone": "0912111001",
                "industries": ["Sản xuất"],
                "regions": ["Miền Bắc"],
                "provinces": ["Hà Nội", "Bắc Ninh"],
                "max_capacity": 50,
                "current_load": 0
            },
            {
                "rep_id": "SALE-02",
                "name": "Trần Thị Bình",
                "email": "binh.tran@namviet-software.vn",
                "phone": "0912111002",
                "industries": ["Bán lẻ"],
                "regions": ["Miền Bắc"],
                "provinces": ["Hà Nội"],
                "max_capacity": 50,
                "current_load": 0
            }
        ]
        self.contact_history = [
            {
                "phone": "0903112233",
                "email": "tung.lam@vietphatlogistics.com",
                "company_name": "Công ty TNHH Vận Tải Việt Phát",
                "status": "DO_NOT_CONTACT",
                "last_contact_date": "2026-10-15",
                "notes": "Khách hàng yêu cầu xóa vĩnh viễn"
            }
        ]
        self.passed = 0
        self.failed = 0

    def assert_true(self, condition, message):
        if not condition:
            raise AssertionError(f"FALSIFIED: {message}")

    def assert_equal(self, actual, expected, message):
        if actual != expected:
            raise AssertionError(f"FAILED: {message} | Expected: '{expected}', Got: '{actual}'")

    def run_test(self, name, func):
        print(f"[*] Running: {name} ...", end=" ")
        try:
            start = time.time()
            func()
            elapsed = (time.time() - start) * 1000
            print(f"[PASSED] ({elapsed:.1f}ms)")
            self.passed += 1
        except Exception as e:
            print(f"[FAILED]\n    Reason: {str(e)}")
            self.failed += 1

    # =========================================================================
    # TEST 1: TRƯỜNG HỢP THÔNG THƯỜNG (STANDARD CASE / HAPPY PATH)
    # =========================================================================
    def test_standard_case_processing(self):
        seg_skill = CustomerSegmentationSkill(self.rules, self.products)
        followup_skill = SalesFollowupSkill(self.sales_team, self.contact_history, self.rules)

        raw_lead = [{
            "lead_id": "TEST-01",
            "source": "Website Form",
            "company_name": "Công ty Cổ phần Thời Trang Hà Nội",
            "contact_name": "Trần Thu Hà",
            "contact_title": "Giám đốc Vận hành",
            "phone": "0912345678",
            "email": "ha.tran@hanoifashion.vn",
            "industry": "Bán lẻ",
            "city": "Hà Nội",
            "inquired_product": "Cần triển khai phần mềm CRM quản lý bán hàng đa kênh",
            "budget": 50000000,
            "company_size": "30 nhân viên",
            "timeline": "Trong vòng 2 tuần tới"
        }]

        # Deduplicate
        masters = seg_skill.deduplicate_leads(raw_lead)
        self.assert_equal(len(masters), 1, "Số khách hàng sau gộp")
        cust = masters[0]

        # Analyze Needs & Gaps
        gaps = seg_skill.analyze_needs_and_gaps(cust)
        self.assert_true(not gaps["is_out_of_scope"], "Không được coi là out of scope")
        self.assert_equal(len(gaps["matched_products"]), 1, "Khớp đúng 1 sản phẩm CRM")
        self.assert_equal(gaps["matched_products"][0]["product_name"], "NamViet CRM Pro", "Tên sản phẩm khớp")
        self.assert_equal(len(gaps["missing_fields"]), 0, "Không thiếu thông tin")

        # Score
        scoring = seg_skill.score_customer(cust, gaps)
        self.assert_equal(scoring["priority"], "P1", "Phải đạt P1 Hot Lead")
        self.assert_true(scoring["total_score"] >= 75, "Điểm phải >= 75")

        # Sales Routing
        assignment = followup_skill.assign_sales_rep(cust)
        self.assert_true(assignment["assigned"], "Phải được gán NVKD")
        self.assert_equal(assignment["rep_id"], "SALE-02", "Gán cho Trần Thị Bình (Bán lẻ / Hà Nội)")

        # Outreach Draft
        draft = followup_skill.generate_outreach_draft(cust, gaps, scoring, assignment)
        self.assert_true("NamViet CRM Pro" in draft["outreach_subject"], "Tiêu đề email chứa tên sản phẩm")
        self.assert_true("Trần Thu Hà" in draft["outreach_body"], "Nội dung email chào đúng tên khách")

    # =========================================================================
    # TEST 2: TRƯỜNG HỢP THIẾU DỮ LIỆU (MISSING DATA CASES)
    # =========================================================================
    def test_missing_data_not_abandoned(self):
        seg_skill = CustomerSegmentationSkill(self.rules, self.products)
        followup_skill = SalesFollowupSkill(self.sales_team, self.contact_history, self.rules)

        raw_lead = [{
            "lead_id": "TEST-MISSING-01",
            "source": "Website Form",
            "company_name": "Xưởng Cơ Khí Tiến Đạt",
            "contact_name": "Bác Đạt",
            "contact_title": "Chủ xưởng",
            "phone": "0987654321",
            "email": None, # Thiếu Email
            "industry": "Sản xuất",
            "city": "Bắc Ninh",
            "inquired_product": "Cần phần mềm ERP quản lý sản xuất cơ khí và kho vật tư",
            "budget": None, # Thiếu Ngân sách
            "company_size": "50 công nhân",
            "timeline": "Càng sớm càng tốt"
        }]

        masters = seg_skill.deduplicate_leads(raw_lead)
        cust = masters[0]
        gaps = seg_skill.analyze_needs_and_gaps(cust)
        
        self.assert_true("Ngân sách dự kiến" in gaps["missing_fields"], "Phát hiện thiếu ngân sách")
        self.assert_true("Email liên hệ chính thức" in gaps["missing_fields"], "Phát hiện thiếu email")
        
        scoring = seg_skill.score_customer(cust, gaps)
        self.assert_true(scoring["priority"] in ["P1", "P2"], "Không bị loại bỏ mà giữ mức tiềm năng cao")
        
        assignment = followup_skill.assign_sales_rep(cust)
        self.assert_equal(assignment["rep_id"], "SALE-01", "Gán cho Nguyễn Văn An (Sản xuất / Bắc Ninh)")

        draft = followup_skill.generate_outreach_draft(cust, gaps, scoring, assignment)
        self.assert_true(len(draft["discovery_questions"]) >= 2, "Sinh ít nhất 2 câu hỏi làm rõ")
        self.assert_true(any("ngân sách" in q.lower() for q in draft["discovery_questions"]), "Có câu hỏi về ngân sách")

    # =========================================================================
    # TEST 3: ĐỐI CHIẾU HỒ SƠ TRÙNG LẶP (DEDUPLICATION & MERGE)
    # =========================================================================
    def test_deduplication_multi_channel_variations(self):
        seg_skill = CustomerSegmentationSkill(self.rules, self.products)

        leads = [
            {
                "lead_id": "L1",
                "company_name": "Công ty Cổ phần Công nghệ Nam Long",
                "phone": "0903456789",
                "email": "thanh@namlongtech.vn",
                "inquired_product": "CRM bán hàng"
            },
            {
                "lead_id": "L2",
                "company_name": "Nam Long Tech JSC",
                "phone": "+84 903 456 789",
                "email": "huong@namlongtech.vn",
                "inquired_product": "HRM nhân sự"
            },
            {
                "lead_id": "L3",
                "company_name": "NL Corp",
                "phone": "0903.456.789",
                "email": "toan@namlongtech.vn",
                "inquired_product": "Quản lý bán hàng"
            }
        ]

        masters = seg_skill.deduplicate_leads(leads)
        self.assert_equal(len(masters), 1, "Gộp 3 đăng ký thành 1 Master Customer")
        self.assert_equal(masters[0]["registration_count"], 3, "Đếm đủ 3 lượt đăng ký")
        self.assert_equal(len(masters[0]["contacts"]), 3, "Lưu đủ 3 đầu mối liên hệ")

    # =========================================================================
    # TEST 4: NGĂN CHẶN CHERRY-PICKING SAI SẢN PHẨM (OUT-OF-SCOPE)
    # =========================================================================
    def test_out_of_scope_high_budget_cherry_picking_prevented(self):
        seg_skill = CustomerSegmentationSkill(self.rules, self.products)

        lead = [{
            "lead_id": "L-DRONE",
            "company_name": "Tập đoàn Đầu tư Alpha",
            "phone": "0945678901",
            "email": "alpha@drone.vn",
            "inquired_product": "Gia công phần mềm nhúng điều khiển drone thiết bị bay",
            "budget": 2500000000 # 2.5 tỷ
        }]

        masters = seg_skill.deduplicate_leads(lead)
        gaps = seg_skill.analyze_needs_and_gaps(masters[0])
        self.assert_true(gaps["is_out_of_scope"], "Phát hiện ngoài phạm vi")

        scoring = seg_skill.score_customer(masters[0], gaps)
        self.assert_equal(scoring["priority"], "OUT_OF_SCOPE", "Xếp OUT_OF_SCOPE")
        self.assert_equal(scoring["breakdown"]["product_fit"]["score"], 0, "Điểm sản phẩm = 0")
        self.assert_equal(scoring["breakdown"]["budget_alignment"]["score"], 0, "Không cộng điểm ngân sách ảo")

    # =========================================================================
    # TEST 5: CHẶN KHÁCH HÀNG DO NOT CONTACT
    # =========================================================================
    def test_do_not_contact_blocking(self):
        followup_skill = SalesFollowupSkill(self.sales_team, self.contact_history, self.rules)

        customer = {
            "customer_id": "CUST-DNC",
            "company_name": "Công ty Vận Tải Việt Phát",
            "contacts": [{"phone": "0903112233", "email": "tung.lam@vietphatlogistics.com"}]
        }

        history_match = followup_skill.check_contact_history(customer)
        self.assert_true(history_match is not None, "Tìm thấy trong lịch sử")
        self.assert_equal(history_match["status"], "DO_NOT_CONTACT", "Trạng thái DO_NOT_CONTACT")

    def run_all(self):
        print("=" * 80)
        print("     BỘ KIỂM THỬ TỰ ĐỘNG AI AGENT (AI301 - ĐỀ 02: CÔNG TY NAM VIỆT)")
        print("=" * 80)
        self.run_test("Test 1: Trường hợp thông thường (Happy Path - Standard Case)", self.test_standard_case_processing)
        self.run_test("Test 2: Trường hợp thiếu dữ liệu (Missing Data & Discovery Questions)", self.test_missing_data_not_abandoned)
        self.run_test("Test 3: Khử trùng & gộp đa kênh, tên viết tắt (Entity Resolution / Dedup)", self.test_deduplication_multi_channel_variations)
        self.run_test("Test 4: Ngăn chặn cherry-picking ngân sách lớn sai sản phẩm (Out-of-Scope)", self.test_out_of_scope_high_budget_cherry_picking_prevented)
        self.run_test("Test 5: Chặn liên hệ theo lịch sử tiếp xúc (Do Not Contact - Blacklist)", self.test_do_not_contact_blocking)
        print("-" * 80)
        print(f"KẾT QUẢ KIỂM THỬ: {self.passed} PASSED | {self.failed} FAILED")
        print("=" * 80)
        return 0 if self.failed == 0 else 1

def run_tests():
    runner = SimpleTestRunner()
    return runner.run_all()

if __name__ == "__main__":
    sys.exit(run_tests())
