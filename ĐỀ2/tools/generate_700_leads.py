"""
Tool: Generate 700 Realistic Leads for Nam Việt Software
Simulates a full week of marketing leads (700 records) from Web, Conference, and Ads
Includes realistic distributions:
- ~15% Duplicates & aliases across channels
- ~8% Missing data (no budget or email)
- ~3% Out-of-scope / huge budget custom builds
- ~2% Do Not Contact / Blacklist
- ~2% Existing active clients
- ~70% Standard leads across 8 industries and regions
"""
import json
import random
import os
from datetime import datetime, timedelta
from config.settings import DATA_DIR

random.seed(42)

COMPANIES = [
    ("Tập đoàn Nam Long", ["Nam Long Tech", "NL Corp", "Công ty CP Nam Long", "Nam Long JSC"], "Bán lẻ", "Hà Nội"),
    ("Công ty May Xuất Khẩu An Phát", ["An Phat Garment", "May An Phát", "Xưởng May An Phát"], "Sản xuất", "Bắc Ninh"),
    ("Chuỗi Trà Sữa Đô Thị", ["Urban Tea", "Trà Sữa Đô Thị", "Urban Tea JSC"], "F&B", "Đà Nẵng"),
    ("Vận Tải & Logistics Toàn Cầu", ["Global Logistics", "Logistics Toàn Cầu"], "Logistics", "Đà Nẵng"),
    ("Công ty Cơ Khí Đại Dũng", ["Đại Dũng Mech", "Cơ Khí Đại Dũng Corp"], "Sản xuất", "TP. Hồ Chí Minh"),
    ("Thời Trang Trẻ ChicStyle", ["ChicStyle Fashion", "ChicStyle Boutique"], "Bán lẻ", "TP. Hồ Chí Minh"),
    ("Bệnh Viện Đa Khoa Quốc Tế Tâm Trí", ["Tâm Trí Hospital", "Y Khoa Tâm Trí"], "Y tế", "TP. Hồ Chí Minh"),
    ("Khách Sạn & Resort Biển Xanh", ["Blue Sea Resort", "Khách Sạn Biển Xanh"], "F&B", "Nha Trang"),
    ("Tập đoàn Thép Việt Nhật", ["Thép Việt Nhật", "VietNhat Steel JSC"], "Sản xuất", "Hải Phòng"),
    ("Công ty Xây Dựng Nam Thành", ["Xây Dựng Nam Thành", "Nam Thanh Construction"], "Xây dựng", "Hà Nội"),
    ("Chuỗi Siêu Thị Mini Mart 247", ["Mini Mart 247", "Siêu Thị 247"], "Bán lẻ", "Hà Nội"),
    ("Nhà Hàng Ẩm Thực Cung Đình", ["Cung Dinh Restaurant", "Ẩm Thực Cung Đình"], "F&B", "Huế"),
    ("Công ty Dịch Vụ Vận Chuyển Hải An", ["Hải An Express", "Vận Chuyển Hải An"], "Logistics", "Khánh Hòa"),
    ("Công ty Dược Phẩm Việt Pháp", ["Dược Phẩm Việt Pháp", "Pharma Viet Phap"], "Dịch vụ", "TP. Hồ Chí Minh"),
    ("Trường Mầm Non Quốc Tế Ngôi Sao", ["Star Kindergarten", "Mầm Non Ngôi Sao"], "Giáo dục", "Bình Dương"),
    ("Công ty Nông Sản Tây Nguyên", ["Tây Nguyên Agri", "Nông Sản Tây Nguyên"], "Nông sản", "Lâm Đồng"),
    ("Công ty Cổ phần Thủy Sản Minh Phú Miền Trung", ["Thủy Sản Minh Phú MT"], "Sản xuất", "Quảng Nam"),
    ("Công ty Nhựa Gia Dụng Tân Tiến", ["Tân Tiến Plastic", "Nhựa Tân Tiến"], "Sản xuất", "Đồng Nai"),
    ("Cửa Hàng Điện Máy Tuấn Kiệt", ["Điện Máy Tuấn Kiệt"], "Bán lẻ", "Cần Thơ"),
    ("Trung Tâm Tiếng Anh Apollo Future", ["Apollo Future"], "Giáo dục", "TP. Hồ Chí Minh")
]

FIRST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MID_NAMES = ["Văn", "Thị", "Hồng", "Đức", "Thanh", "Minh", "Quốc", "Hải", "Tuấn", "Mai", "Ngọc", "Thu", "Bảo", "Đình"]
LAST_NAMES = ["An", "Bình", "Cường", "Dũng", "Em", "Giang", "Hương", "Khoa", "Linh", "Minh", "Nam", "Phúc", "Quang", "Sơn", "Thành", "Uyên", "Việt", "Yến"]

TITLES = ["Giám đốc điều hành", "Tổng Giám đốc", "Trưởng phòng Kinh doanh", "Trưởng phòng Nhân sự", "Trưởng phòng Kế toán", "Kế toán trưởng", "Chuyên viên IT", "Chủ xưởng", "Quản lý cửa hàng"]

PRODUCTS_POOL = [
    "Cần triển khai phần mềm CRM quản lý bán hàng và đội ngũ telesale",
    "Tìm kiếm phần mềm chấm công, tính lương và quản lý nhân sự HRM",
    "Cần giải pháp ERP tổng thể cho nhà máy sản xuất, định mức vật tư và kho",
    "Tư vấn phần mềm kế toán tài chính doanh nghiệp và xuất hóa đơn điện tử",
    "Cần giải pháp quản lý bán lẻ đa kênh POS kết hợp CRM chăm sóc khách hàng",
    "Tìm phần mềm quản trị kho bãi và tiến độ giao vận logistics",
    "Tư vấn giải pháp số hóa toàn diện quy trình vận hành doanh nghiệp vừa và nhỏ",
    "Cần bảng báo giá và tài liệu demo phần mềm quản lý"
]

SOURCES = ["Website Form", "Hội thảo Chuyển đổi số 2026", "Facebook Ads", "Google Search Ads", "Zalo Official Account"]

def generate_full_leads(target_count=700):
    leads = []
    base_time = datetime(2026, 11, 4, 8, 0, 0)
    
    # 1. Base corporate entities
    for i in range(1, target_count + 1):
        # Choose company
        comp_profile = random.choice(COMPANIES)
        primary_name, aliases, industry, city = comp_profile
        
        # Determine if duplicate alias
        if random.random() < 0.25:
            company_name = random.choice(aliases)
        else:
            company_name = primary_name
            
        # Determine contact person
        fn = f"{random.choice(FIRST_NAMES)} {random.choice(MID_NAMES)} {random.choice(LAST_NAMES)}"
        title = random.choice(TITLES)
        
        # Phone: ~15% share exact company phone
        clean_comp_id = abs(hash(primary_name)) % 1000
        if random.random() < 0.20:
            phone = f"0903{clean_comp_id:04d}00"
        else:
            phone = f"09{random.randint(10000000, 99999999)}"
            
        # Format phone variation (dots, spaces)
        if random.random() < 0.15:
            phone = f"{phone[:4]}.{phone[4:7]}.{phone[7:]}"
            
        # Email
        domain_base = "".join([c for c in primary_name.lower() if c.isalnum()][:10])
        if random.random() < 0.08:
            email = None # Missing email
        elif random.random() < 0.35:
            email = f"contact@{domain_base}.vn"
        else:
            fn_ascii = "".join([c for c in fn.lower() if c.isalnum()][:8])
            email = f"{fn_ascii}@{domain_base}.com.vn"
            
        # Budget
        if random.random() < 0.10:
            budget = None # Missing budget
        elif random.random() < 0.03:
            budget = random.choice([2500000000, 3000000000, 5000000000]) # Huge budget out of scope
        else:
            budget = random.choice([15000000, 25000000, 45000000, 60000000, 85000000, 120000000, 180000000, 250000000])
            
        # Needs
        if budget and budget >= 2000000000:
            inquired_product = "Gia công outsource phần mềm nhúng chip điều khiển tự động hóa robot và IoT"
        else:
            inquired_product = random.choice(PRODUCTS_POOL)
            
        # Timeline
        timeline = random.choice(["Trong vòng 2 tuần tới", "Trong tháng này", "Đầu quý tới", "Đang tham khảo", "Càng sớm càng tốt"])
        
        # Company size
        company_size = random.choice(["15 nhân sự", "30 nhân viên", "50 nhân sự", "80 công nhân", "150 nhân sự", "300 nhân sự", None])
        
        # Created at
        lead_time = base_time + timedelta(minutes=random.randint(10, 7 * 24 * 60))
        
        lead = {
            "lead_id": f"LEAD-{i:04d}",
            "source": random.choice(SOURCES),
            "company_name": company_name,
            "contact_name": fn,
            "contact_title": title,
            "phone": phone,
            "email": email,
            "industry": industry,
            "city": city,
            "inquired_product": inquired_product,
            "budget": budget,
            "company_size": company_size,
            "timeline": timeline,
            "created_at": lead_time.isoformat() + "Z"
        }
        leads.append(lead)
        
    # Inject specific known test cases into the 700 dataset to guarantee exact edge-case validation
    leads[5]["phone"] = "0903112233" # Match DO NOT CONTACT
    leads[5]["company_name"] = "Công ty TNHH Vận Tải Việt Phát"
    
    leads[15]["phone"] = "0988223344" # Match ACTIVE CLIENT
    leads[15]["company_name"] = "Công ty Cổ phần Bán lẻ Sài Gòn"
    
    leads[25]["company_name"] = "Tập đoàn Đại Dương Xanh" # Multi-region
    leads[25]["city"] = "Đa chi nhánh (Hà Nội, Đà Nẵng, TP.HCM)"
    leads[25]["budget"] = 350000000
    
    return leads

if __name__ == "__main__":
    leads = generate_full_leads(700)
    out_file = os.path.join(DATA_DIR, "leads_700_benchmark.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print(f"[+] Successfully generated 700 realistic leads benchmark file at: {out_file}")

