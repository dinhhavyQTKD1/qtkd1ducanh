# HỆ THỐNG AI AGENT SÀNG LỌC & ĐIỀU PHỐI KHÁCH HÀNG TIỀM NĂNG
## CÔNG TY CỔ PHẦN PHẦN MỀM NAM VIỆT (AI301 – ĐỀ 02)

Dự án phát triển giải pháp AI Agent tự hành giải quyết bài toán tiếp nhận 700 khách hàng tiềm năng mỗi tuần, khử trùng lặp đa kênh, phân loại nhu cầu, chấm điểm ưu tiên, kiểm soát lịch sử tiếp xúc, điều phối thông minh cho 8 Nhân viên Kinh doanh (NVKD) và hỗ trợ Human-in-the-Loop cho Trưởng phòng Kinh doanh.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```text
c:\Users\TGPM\Downloads\ĐỀ2\
│
├── run.bat                          # Script chạy 1-click cho người dùng / Giảng viên
├── run_python.bat                   # Wrapper gọi môi trường Python chuẩn
├── main.py                          # Điểm khởi chạy (Entry point) toàn bộ hệ thống
│
├── config/                          # Cấu hình & Quy tắc nghiệp vụ
│   ├── business_rules.json          # Quy tắc de-dupe, trọng số chấm điểm, ngưỡng leo thang
│   └── settings.py                  # Quản lý đường dẫn và tải cấu hình
│
├── data/                            # Bộ dữ liệu đầu vào chuẩn hóa
│   ├── leads_input.json             # Hồ sơ đăng ký từ Web, Hội thảo, Ads (gồm các ca thử nghiệm)
│   ├── contact_history.json         # Lịch sử tiếp xúc (Do Not Call, Đang chăm sóc, Khiếu nại...)
│   ├── sales_team.json              # Danh sách 8 Nhân viên Kinh doanh & ma trận phụ trách
│   └── products.json                # Danh mục 4 dòng sản phẩm chính của Nam Việt
│
├── skills/                          # 2 Kỹ năng nghiệp vụ cốt lõi theo đề bài
│   ├── __init__.py
│   ├── customer_segmentation.py     # Kỹ năng 1: Khử trùng, Phân tích nhu cầu & Chấm điểm ưu tiên
│   └── sales_followup.py            # Kỹ năng 2: Phân công thông minh, Lọc DNC & Soạn Outreach
│
├── agent/                           # Kiến trúc AI Agent Orchestrator & Audit Trail
│   ├── __init__.py
│   ├── orchestrator.py              # Bộ điều phối quy trình (Workflow Engine)
│   └── audit_logger.py              # Hệ thống ghi vết kiểm toán chi tiết (Audit Trail)
│
├── outputs/                         # Kết quả đầu ra tự động sinh
│   ├── master_customers.json        # Danh sách khách hàng hợp nhất (sau khử trùng lặp)
│   ├── master_customers.csv         # File CSV phục vụ import CRM / Excel
│   ├── sales_task_assignments.json  # Danh sách công việc chi tiết cho 8 NVKD
│   ├── sales_task_assignments.csv   # File CSV danh sách công việc theo NVKD
│   ├── manager_escalations.json     # Các ca cần Trưởng phòng KD quyết định
│   ├── do_not_contact.json          # Danh sách khách hàng không được phép liên hệ lại
│   ├── summary_report.json          # Thống kê tổng hợp số lượng (không đếm lặp)
│   ├── summary_report.md            # Báo cáo tổng hợp định dạng Markdown
│   ├── audit_trail.log              # File nhật ký thực thi dạng text
│   └── execution_log.json           # File nhật ký thực thi cấu trúc JSON
│
├── tests/                           # Bộ kiểm thử tự động
│   ├── __init__.py
│   └── test_suite.py                # Kiểm thử ca thông thường, thiếu dữ liệu, ranh giới
│
├── web/                             # Bảng điều khiển trực quan (Dashboard)
│   ├── generate_dashboard.py        # Script tạo HTML Dashboard tự động
│   └── dashboard.html               # Giao diện web trực quan trình chiếu cho Giảng viên
│
├── REPORT_TASK1_TASK2.md            # Báo cáo đồ án chi tiết (Hoàn thành Task 1 & Task 2)
└── README.md                        # Hướng dẫn cài đặt và sử dụng
```

---

## 🚀 HƯỚNG DẪN CHẠY VÀ SỬ DỤNG

### 1. Chạy quy trình AI Agent chính (Full Pipeline)
Bạn chỉ cần thực hiện 1 trong 2 cách sau:

- **Cách 1 (Khuyên dùng - 1 Click):** Kích đúp vào file `run.bat` trên Windows.
- **Cách 2 (Qua dòng lệnh PowerShell / CMD):**
  ```powershell
  .\run_python.bat main.py
  ```

Hệ thống sẽ tự động:
1. Đọc dữ liệu đầu vào từ `data/leads_input.json`.
2. Đối chiếu thực thể và khử trùng lặp (Entity Resolution).
3. Phân tích khoảng trống thông tin và chấm điểm ưu tiên (P1, P2, P3, Out-of-Scope).
4. Kiểm tra lịch sử tiếp xúc (loại trừ Do-Not-Contact, chuyển khách hiện hữu cho CSKH).
5. Phân bổ công việc chuẩn xác cho 8 NVKD theo ma trận Ngành và Khu vực.
6. Soạn thảo bản nháp thông điệp tiếp cận (email demo hoặc bộ câu hỏi bổ sung).
7. Xuất đầy đủ các file JSON, CSV, Markdown trong thư mục `outputs/`.
8. Tự động cập nhật bảng điều khiển trực quan `web/dashboard.html`.

---

### 2. Xem Bảng Điều Khiển Trực Quan Trên Localhost (Interactive Pastel Pink Dashboard)
Hệ thống cung cấp sẵn máy chủ web Localhost tích hợp (Python standard library, không cần cài đặt thêm thư viện):

- **Khởi động Localhost chính (Port 8000):**
  - Kích đúp vào file `start_localhost.bat` (hoặc chạy: `.\run_python.bat server.py`)
  - Mở trình duyệt web truy cập: **`http://localhost:8000`**
- **Khởi động Localhost thứ 2 độc lập (Port 8080):**
  - Kích đúp vào file `start_localhost_8080.bat` (hoặc chạy: `.\run_python.bat server.py 8080`)
  - Mở trình duyệt web truy cập: **`http://localhost:8080`**
- **Trình chiếu Slide báo cáo thuyết trình:**
  - Truy cập trực tiếp: **`http://localhost:8000/presentation`** (7 slides thuyết trình Task 1 & Task 2)

**Các tính năng nổi bật trên giao diện Dashboard:**
- **Băng tiến trình luồng 5 bước kết nối mũi tên (Pipeline Stepper):** Hiển thị trực quan toàn bộ tiến trình từ Tiếp nhận -> Khử trùng -> Phân loại -> Điều phối -> Escalation, bấm vào bước nào sẽ kích hoạt tab tương ứng.
- **Tab 1: Khách hàng sau đối chiếu:** Toàn bộ hồ sơ hợp nhất, chip lọc nhanh (P1, P2, P3, Out-of-Scope, DNC), nút xem bản nháp thư mời & bộ câu hỏi đào sâu thông tin còn thiếu.
- **Tab 2: Sơ đồ quy trình 6 bước:** Mô phỏng đồ họa chính xác 100% sơ đồ quy trình từ Đề án AI301 Đề 02 kèm hình thoi quyết định và 2 điểm Human-in-the-Loop.
- **Tab 3: Đội ngũ 8 NVKD:** 8 thẻ gradient pastel hiển thị số khách nhận, hạn mức và phân bổ không đếm lặp (Click vào thẻ để lọc công việc của từng NVKD).
- **Tab 4: Trưởng phòng quyết định (Escalations):** Phòng xử lý ngoại lệ với nút [✔ Duyệt Phân Công] hoạt động trực tiếp.
- **Tab 5: Danh sách chặn (Do Not Contact):** Bảo vệ an toàn tiếp thị, tránh vi phạm gọi khách blacklist.
- **Tab 6: Nhật ký kiểm toán (Audit Trail):** Truy vết minh bạch từng rule ID, hành động và payload dữ liệu.
- **Tab 7: Tóm tắt đồ án & Hướng dẫn Localhost:** Giải thích tường minh Task 1 & Task 2 cho Giảng viên.

---

### 3. Chạy Bộ Kiểm Thử Tự Động (Automated Test Suite)
Chạy lệnh sau để kiểm thử 5 kịch bản tự động (ca thông thường, thiếu dữ liệu, ranh giới quy tắc, khử trùng, chặn DNC):
```powershell
.\run_python.bat tests/test_suite.py
```

---

### 4. Hướng dẫn nạp bộ dữ liệu mới của Giảng viên tại buổi thi
Khi Giảng viên cung cấp một file JSON dữ liệu mới:
```powershell
.\run_python.bat main.py --leads "duong_dan_file_moi.json"
```
Hệ thống sẽ chạy nạp trực tiếp, không sửa dữ liệu, xuất toàn bộ kết quả mới ra màn hình console và cập nhật `web/dashboard.html` trong 2 giây!

