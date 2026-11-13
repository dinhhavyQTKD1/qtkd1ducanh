"""
Skill: customer_segmentation
Responsibilities:
1. Normalize, resolve entities, and deduplicate leads across sources.
2. Analyze customer needs, detect missing information (Information Gaps).
3. Score leads multi-dimensionally and assign priority levels (P1-Hot, P2-Warm, P3-Cold, Out-of-Scope).
"""
import re
import difflib
import uuid
from typing import List, Dict, Any, Tuple

class CustomerSegmentationSkill:
    def __init__(self, rules: Dict[str, Any], products: List[Dict[str, Any]], logger=None):
        self.rules = rules
        self.products = products
        self.logger = logger
        self.dedup_cfg = rules.get("deduplication", {})
        self.scoring_cfg = rules.get("scoring", {})

    # ---------------------------
    # 1. NORMALIZATION UTILITIES
    # ---------------------------
    def normalize_phone(self, phone: str) -> str:
        if not phone:
            return ""
        clean = re.sub(r"[^\d]", "", str(phone))
        if clean.startswith("84") and len(clean) >= 11:
            clean = "0" + clean[2:]
        return clean

    def normalize_email(self, email: str) -> Tuple[str, str]:
        if not email:
            return "", ""
        clean = str(email).strip().lower()
        parts = clean.split("@")
        domain = parts[1] if len(parts) > 1 else ""
        return clean, domain

    def clean_company_name(self, name: str) -> str:
        if not name:
            return ""
        clean = str(name).strip().lower()
        patterns = self.dedup_cfg.get("company_name_clean_patterns", [])
        for p in patterns:
            # Replace common company abbreviations and type descriptors
            clean = re.sub(r"\b" + re.escape(p) + r"\b", "", clean)
        clean = re.sub(r"[^\w\s]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    def is_public_domain(self, domain: str) -> bool:
        public_domains = self.dedup_cfg.get("public_email_domains", [])
        return domain in public_domains or not domain

    def are_companies_similar(self, name1: str, name2: str) -> bool:
        c1 = self.clean_company_name(name1)
        c2 = self.clean_company_name(name2)
        if not c1 or not c2:
            return False
        if c1 == c2:
            return True
        # Check acronym matching (e.g., Nam Long -> NL)
        words1 = c1.split()
        words2 = c2.split()
        acronym1 = "".join([w[0] for w in words1 if w])
        acronym2 = "".join([w[0] for w in words2 if w])
        if (c1 in c2 or c2 in c1) and (len(c1) >= 4 or len(c2) >= 4):
            return True
        if acronym1 == c2 or acronym2 == c1:
            return True

        similarity = difflib.SequenceMatcher(None, c1, c2).ratio()
        threshold = self.dedup_cfg.get("similarity_threshold", 0.85)
        return similarity >= threshold

    # ---------------------------
    # 2. DEDUPLICATION & MERGING
    # ---------------------------
    def deduplicate_leads(self, raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        clusters: List[List[Dict[str, Any]]] = []
        
        # Fast Inverted Index for O(1) matching
        phone_index: Dict[str, int] = {}
        domain_index: Dict[str, int] = {}
        company_exact_index: Dict[str, int] = {}

        for lead in raw_leads:
            lead_phone = self.normalize_phone(lead.get("phone"))
            lead_email, lead_domain = self.normalize_email(lead.get("email"))
            lead_company = lead.get("company_name", "")
            lead_company_clean = self.clean_company_name(lead_company)

            matched_cluster_idx = None

            # 1. Fast Phone Match O(1)
            if lead_phone and lead_phone in phone_index:
                matched_cluster_idx = phone_index[lead_phone]

            # 2. Fast Corporate Email Domain Match O(1)
            elif lead_domain and not self.is_public_domain(lead_domain) and lead_domain in domain_index:
                matched_cluster_idx = domain_index[lead_domain]

            # 3. Fast Normalized Company Exact Match O(1)
            elif lead_company_clean and lead_company_clean in company_exact_index:
                matched_cluster_idx = company_exact_index[lead_company_clean]

            # 4. Fallback Fuzzy Match across existing clusters (only if fast lookups miss)
            else:
                for idx, cluster in enumerate(clusters):
                    representative = cluster[0]
                    rep_company = representative.get("company_name", "")
                    if self.are_companies_similar(lead_company, rep_company):
                        lead_city = (lead.get("city") or "").lower()
                        rep_city = (representative.get("city") or "").lower()
                        if (lead_city and rep_city and (lead_city in rep_city or rep_city in lead_city)) or (not lead_city or not rep_city):
                            matched_cluster_idx = idx
                            break

            if matched_cluster_idx is not None:
                clusters[matched_cluster_idx].append(lead)
                # Update indexes for this cluster
                if lead_phone:
                    phone_index[lead_phone] = matched_cluster_idx
                if lead_domain and not self.is_public_domain(lead_domain):
                    domain_index[lead_domain] = matched_cluster_idx
                if lead_company_clean:
                    company_exact_index[lead_company_clean] = matched_cluster_idx

                if self.logger:
                    self.logger.log(
                        step="DEDUPLICATION",
                        action="MERGE_LEAD_INTO_EXISTING_CLUSTER",
                        rule_id="RULE_DEDUP_MULTI_ATTR",
                        details={
                            "lead_id": lead.get("lead_id"),
                            "company": lead.get("company_name"),
                            "phone": lead.get("phone"),
                            "matched_cluster_lead_id": clusters[matched_cluster_idx][0].get("lead_id")
                        }
                    )
            else:
                new_idx = len(clusters)
                clusters.append([lead])
                if lead_phone:
                    phone_index[lead_phone] = new_idx
                if lead_domain and not self.is_public_domain(lead_domain):
                    domain_index[lead_domain] = new_idx
                if lead_company_clean:
                    company_exact_index[lead_company_clean] = new_idx

                if self.logger:
                    self.logger.log(
                        step="DEDUPLICATION",
                        action="CREATE_NEW_CUSTOMER_CLUSTER",
                        rule_id="RULE_DEDUP_NEW_ENTITY",
                        details={
                            "lead_id": lead.get("lead_id"),
                            "company": lead.get("company_name"),
                            "phone": lead.get("phone")
                        }
                    )

        # Merge clusters into unified Master Customer records
        master_customers = []
        for idx, cluster in enumerate(clusters, start=1):
            master_cust = self._merge_cluster(cluster, f"CUST-NV-{idx:04d}")
            master_customers.append(master_cust)

        return master_customers

    def _merge_cluster(self, cluster: List[Dict[str, Any]], customer_id: str) -> Dict[str, Any]:
        source_lead_ids = [c.get("lead_id") for c in cluster]
        sources = list(set([c.get("source", "Unknown") for c in cluster]))
        
        # Primary company name: select the longest / most formal one
        company_names = [c.get("company_name", "") for c in cluster if c.get("company_name")]
        company_names.sort(key=lambda x: len(x), reverse=True)
        primary_company = company_names[0] if company_names else "Doanh nghiệp chưa đặt tên"

        # Contacts list
        contacts = []
        for c in cluster:
            contact = {
                "name": c.get("contact_name") or "Đại diện công ty",
                "title": c.get("contact_title") or "Người liên hệ",
                "phone": c.get("phone") or "",
                "email": c.get("email") or "",
                "source": c.get("source")
            }
            if contact not in contacts:
                contacts.append(contact)

        # Inquired needs aggregation
        inquired_texts = [c.get("inquired_product", "") for c in cluster if c.get("inquired_product")]
        consolidated_needs = " | ".join(list(set(inquired_texts)))

        # Budgets
        budgets = [c.get("budget") for c in cluster if c.get("budget") is not None]
        max_budget = max(budgets) if budgets else None

        # Industry
        industries = [c.get("industry") for c in cluster if c.get("industry")]
        primary_industry = industries[0] if industries else "Chưa xác định"

        # City / Region
        cities = [c.get("city") for c in cluster if c.get("city")]
        primary_city = cities[0] if cities else "Chưa xác định"

        # Timeline
        timelines = [c.get("timeline") for c in cluster if c.get("timeline")]
        consolidated_timeline = timelines[0] if timelines else "Chưa xác định"

        # Company size
        sizes = [c.get("company_size") for c in cluster if c.get("company_size")]
        consolidated_size = sizes[0] if sizes else "Chưa xác định"

        return {
            "customer_id": customer_id,
            "company_name": primary_company,
            "all_company_aliases": list(set(company_names)),
            "source_lead_ids": source_lead_ids,
            "source_channels": sources,
            "registration_count": len(cluster),
            "contacts": contacts,
            "primary_contact": contacts[0] if contacts else {},
            "industry": primary_industry,
            "city": primary_city,
            "consolidated_needs": consolidated_needs,
            "budget": max_budget,
            "company_size": consolidated_size,
            "timeline": consolidated_timeline
        }

    # ---------------------------
    # 3. NEEDS & GAP ANALYSIS
    # ---------------------------
    def analyze_needs_and_gaps(self, customer: Dict[str, Any]) -> Dict[str, Any]:
        needs_text = (customer.get("consolidated_needs") or "").lower()
        matched_products = []
        is_out_of_scope = False
        out_of_scope_reason = None

        # Check out-of-scope keywords (custom drone, embedded iot, outsource game, etc.)
        out_of_scope_keywords = ["drone", "thiết bị bay", "nhúng", "iot công nghiệp nhúng", "gia công outsource", "game"]
        for kw in out_of_scope_keywords:
            if kw in needs_text:
                is_out_of_scope = True
                out_of_scope_reason = f"Yêu cầu '{kw}' không nằm trong danh mục giải pháp đóng gói quản trị SME của Nam Việt"
                break

        # Match with Nam Việt product portfolio
        for prod in self.products:
            score = 0
            for kw in prod.get("keywords", []):
                if kw.lower() in needs_text:
                    score += 1
            if score > 0:
                matched_products.append({
                    "product_id": prod["product_id"],
                    "product_name": prod["name"],
                    "category": prod["category"],
                    "min_budget": prod["min_budget"],
                    "max_budget": prod["max_budget"],
                    "match_intensity": score
                })

        # Identify missing information fields
        missing_fields = []
        if not customer.get("budget"):
            missing_fields.append("Ngân sách dự kiến")
        if customer.get("industry") == "Chưa xác định":
            missing_fields.append("Lĩnh vực hoạt động cụ thể")
        if customer.get("city") == "Chưa xác định":
            missing_fields.append("Khu vực / Tỉnh thành")
        if customer.get("company_size") == "Chưa xác định":
            missing_fields.append("Quy mô nhân sự / Điểm bán")
        if customer.get("timeline") == "Chưa xác định":
            missing_fields.append("Lộ trình triển khai dự kiến")

        # Check contact validity
        has_valid_email = any(c.get("email") for c in customer.get("contacts", []))
        has_valid_phone = any(self.normalize_phone(c.get("phone")) for c in customer.get("contacts", []))
        if not has_valid_email:
            missing_fields.append("Email liên hệ chính thức")
        if not has_valid_phone:
            missing_fields.append("Số điện thoại liên hệ")

        analysis_result = {
            "matched_products": matched_products,
            "is_out_of_scope": is_out_of_scope,
            "out_of_scope_reason": out_of_scope_reason,
            "missing_fields": missing_fields,
            "has_missing_info": len(missing_fields) > 0
        }

        if self.logger:
            self.logger.log(
                step="NEEDS_AND_GAP_ANALYSIS",
                action="ANALYZE_NEEDS",
                rule_id="RULE_PRODUCT_KEYWORD_MATCH",
                details={
                    "customer_id": customer["customer_id"],
                    "matched_count": len(matched_products),
                    "matched_product_names": [p["product_name"] for p in matched_products],
                    "is_out_of_scope": is_out_of_scope,
                    "missing_fields": missing_fields
                }
            )

        return analysis_result

    # ---------------------------
    # 4. LEAD SCORING & PRIORITIZATION
    # ---------------------------
    def score_customer(self, customer: Dict[str, Any], gap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        weights = self.scoring_cfg.get("weights", {"product_fit": 40, "budget_alignment": 30, "authority_and_timeline": 20, "data_completeness": 10})
        thresholds = self.scoring_cfg.get("thresholds", {"p1_hot": 75, "p2_warm": 50, "p3_cold": 30})

        # 1. Product Fit Score (Max 40)
        fit_score = 0
        fit_breakdown = ""
        if gap_analysis["is_out_of_scope"]:
            fit_score = 0
            fit_breakdown = "0/40 (Yêu cầu nằm ngoài danh mục sản phẩm Nam Việt)"
        elif len(gap_analysis["matched_products"]) > 0:
            fit_score = 40
            names = ", ".join([p["product_name"] for p in gap_analysis["matched_products"]])
            fit_breakdown = f"40/40 (Khớp trực tiếp với sản phẩm: {names})"
        else:
            fit_score = 20
            fit_breakdown = "20/40 (Nhu cầu số hóa chung chung, chưa chỉ định rõ module)"

        # 2. Budget Alignment Score (Max 30)
        budget_score = 0
        budget_breakdown = ""
        b = customer.get("budget")
        if gap_analysis["is_out_of_scope"]:
            budget_score = 0
            budget_breakdown = "0/30 (Ngân sách lớn nhưng sai sản phẩm, không tính điểm ưu tiên)"
        elif b is not None:
            # Check against matched products
            if gap_analysis["matched_products"]:
                min_req = min([p["min_budget"] for p in gap_analysis["matched_products"]])
                max_req = max([p["max_budget"] for p in gap_analysis["matched_products"]]) * 1.5
                if b >= min_req and b <= max_req:
                    budget_score = 30
                    budget_breakdown = f"30/30 (Ngân sách {b:,.0f} VNĐ nằm chuẩn trong khung đầu tư giải pháp)"
                elif b < min_req:
                    budget_score = 10
                    budget_breakdown = f"10/30 (Ngân sách {b:,.0f} VNĐ thấp hơn mức tối thiểu {min_req:,.0f} VNĐ)"
                else:
                    budget_score = 25
                    budget_breakdown = f"25/30 (Ngân sách {b:,.0f} VNĐ dồi dào, cần phân tích kỹ phạm vi)"
            else:
                budget_score = 20
                budget_breakdown = f"20/30 (Ngân sách {b:,.0f} VNĐ có sẵn)"
        else:
            budget_score = 15
            budget_breakdown = "15/30 (Chưa công bố ngân sách, đang ở giai đoạn tham khảo)"

        # 3. Authority & Timeline Score (Max 20)
        auth_score = 0
        auth_breakdown = ""
        titles = " ".join([c.get("title", "") for c in customer.get("contacts", [])]).lower()
        timeline = str(customer.get("timeline", "")).lower()

        is_decision_maker = any(k in titles for k in ["giám đốc", "ceo", "chủ tịch", "chủ xưởng", "chủ thương hiệu", "founder", "trưởng phòng", "bác sĩ"])
        is_urgent = any(k in timeline for k in ["2 tuần", "ngay", "trong tháng", "gấp", "sớm", "trong tuần"])

        if is_decision_maker and is_urgent:
            auth_score = 20
            auth_breakdown = "20/20 (Người liên hệ có thẩm quyền cao + Nhu cầu triển khai gấp)"
        elif is_decision_maker or is_urgent:
            auth_score = 15
            auth_breakdown = "15/20 (Người liên hệ có thẩm quyền hoặc có tiến độ rõ ràng)"
        else:
            auth_score = 10
            auth_breakdown = "10/20 (Cấp nhân viên hoặc timeline dài hạn/chưa xác định)"

        # 4. Data Completeness Score (Max 10)
        missing_count = len(gap_analysis["missing_fields"])
        if missing_count == 0:
            comp_score = 10
            comp_breakdown = "10/10 (Hồ sơ đầy đủ mọi trường thông tin trọng yếu)"
        elif missing_count <= 2:
            comp_score = 7
            comp_breakdown = f"7/10 (Thiếu {missing_count} trường: {', '.join(gap_analysis['missing_fields'])})"
        else:
            comp_score = 3
            comp_breakdown = f"3/10 (Thiếu nhiều thông tin: {', '.join(gap_analysis['missing_fields'])})"

        total_score = fit_score + budget_score + auth_score + comp_score

        # Priority determination
        if gap_analysis["is_out_of_scope"]:
            priority = "OUT_OF_SCOPE"
            priority_label = "Không phù hợp (Ngoài phạm vi sản phẩm)"
        elif total_score >= thresholds["p1_hot"]:
            priority = "P1"
            priority_label = "P1 - Rất tiềm năng (Hot Lead)"
        elif total_score >= thresholds["p2_warm"]:
            priority = "P2"
            priority_label = "P2 - Tiềm năng (Warm Lead)"
        elif total_score >= thresholds["p3_cold"]:
            priority = "P3"
            priority_label = "P3 - Cần nuôi dưỡng (Cold Lead)"
        else:
            priority = "UNQUALIFIED"
            priority_label = "Chưa đạt chuẩn (Unqualified)"

        scoring_result = {
            "total_score": total_score,
            "priority": priority,
            "priority_label": priority_label,
            "breakdown": {
                "product_fit": {"score": fit_score, "explanation": fit_breakdown},
                "budget_alignment": {"score": budget_score, "explanation": budget_breakdown},
                "authority_and_timeline": {"score": auth_score, "explanation": auth_breakdown},
                "data_completeness": {"score": comp_score, "explanation": comp_breakdown}
            }
        }

        if self.logger:
            self.logger.log(
                step="SCORING_AND_PRIORITIZATION",
                action="SCORE_CUSTOMER",
                rule_id="RULE_MULTI_DIMENSIONAL_SCORING",
                details={
                    "customer_id": customer["customer_id"],
                    "company_name": customer["company_name"],
                    "total_score": total_score,
                    "priority": priority,
                    "breakdown": {k: v["score"] for k, v in scoring_result["breakdown"].items()}
                }
            )

        return scoring_result

